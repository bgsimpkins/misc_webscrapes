require(XML)
require(RCurl)
require(RMySQL)

setwd("/home/bsimpkins/Documents/R/Darklyrics_scrape/")
rootURL <- "http://www.darklyrics.com/"

########################################Functions

getArtistsForLetter <- function(letter)
{
  letter <- tolower(letter)
  url <- paste(rootURL,letter,".html",sep="")
  html <- getURL(url)
  doc <- htmlParse(html,asText = T)
  links <- xpathSApply(doc,"//a/@href")
  
  sel <- grep(paste(letter,"\\/.*html",sep=""),links)    
  links <- links[sel]

  ##Can still have links to external pages. Need to remove those.
  sel <- grep("http",links)
  links <- links[-sel]
  
  artistNodes <- sapply(links, function(x){
    xpathSApply(doc,paste("//a[@href='",x,"']",sep=""))
  })
  
  res <- sapply(artistNodes,function(x){ 
    c(xmlAttrs(x)["href"],name=xmlValue(x))  
  })
  colnames(res) <- NULL
  as.data.frame(t(res))
}
###################################End Functions

getAlbumsForArtist <- function(artistPage)
{
  html <- getURL(artistPage)
  doc <- htmlParse(html,asText = T)
  albumDivs <- xpathSApply(doc,paste("//div[@class='album']",sep=""))

  albums <- sapply(albumDivs,function(x){
    path <- xmlAttrs(xpathSApply(x,"a")[[1]])["href"]
    label <- xpathSApply(x,"h2")
    name <- xpathSApply(label[[1]],"strong")
    name <- xmlValue(name[[1]])
    typeYear <- gsub(name,"",xmlValue(label[[1]]),fixed=T)
    tysplit <- unlist(strsplit(typeYear, ": *"))
    year <- substring(tysplit[2],2,nchar(tysplit[2])-1)
    name <- substring(name,2,nchar(name)-1)
    
    c(path,name=name,type=tysplit[1],year=year)
  })
  albums <- as.data.frame(t(albums))
  albums$albumNo <- seq(1:nrow(albums))
  
  ##Probably should move some of the processing that can be done as vectors from the sapply above...
  albums$href <- gsub("../","",albums$href,fixed = T)
  albums$href <- gsub("#1","",albums$href,fixed = T)
  
  albums
}


getLyricsForAlbum <- function(albumPage)
{
  html <- getURL(albumPage)
  doc <- htmlParse(html,asText = T)
  songHeaders <- xpathSApply(doc,"//h3")
  
  songFrame <- data.frame()
  notesFrame <- data.frame()
  #lyrics <- sapply(songHeaders,function(songHeader)
  for (songHeader in songHeaders)
  {
    ###UNCOMMENT
    
    nextHTML <- xpathSApply(songHeader,"following-sibling::node()")
    
    credit <- NA
    headerA <- xpathSApply(songHeader,"a")[[1]]
    songNo <- xmlGetAttr(headerA,"name")
    title <- unlist(strsplit(xmlValue(headerA),paste(songNo,"\\. *",sep="")))[[2]]
    
    lineNo <- 1
    for (i in 1:length(nextHTML))
    {
      node <- nextHTML[[i]]
      val <- xmlValue(node)
      if (xmlName(node) == "i"){
        note <- xmlValue(node)
        note <- gsub("[","",note,fixed=T)
        note <- gsub("]","",note,fixed=T)

        notesFrame <- rbind(notesFrame,data.frame(songNo,noteLine=i,note))
      }else if (xmlName(node) %in% c("h3","div")) {
        break
      }else if (val != ""){
        val <- gsub("\n","",val)
        val <- gsub("\"","",val)
        songFrame <- rbind(songFrame,data.frame(songNo=songNo,title=title,lineNo=lineNo,line=val))
        lineNo <- lineNo + 1
      }
    }
  }
  list(songLines=songFrame,notes=notesFrame)
}

importAlbumLyrics <- function(songLines, artistName, albumNo, albumTitle, notes=NULL,overwrite=FALSE)
{
  songLines$title <- sapply(songLines$title,as.character)
  songLines$line <- sapply(songLines$line,as.character)
  
  conn <- dbConnect(MySQL(), user="bsimpkins", 
      password="yourmomma",
      dbname="lyric_database", 
      host="192.168.0.11")
  
  ##Check if artist exists. If so, get id. If not, add.
  res <- dbGetQuery(conn, paste("SELECT artistId FROM Artist WHERE artistName = '",artistName,"'",sep=""))
  if (nrow(res) == 0)
  {
    dbSendQuery(conn, paste("INSERT INTO Artist (artistName) VALUES ('",artistName,"')",sep=""))
  }
  
  res <- dbGetQuery(conn, paste("SELECT artistId FROM Artist WHERE artistName = '",artistName,"'",sep=""))
  artistId <- res["artistId"]
  
  ##Check to see if album exists
  res <- dbGetQuery(conn, paste("SELECT albumId FROM Album WHERE artistId = ",artistId," AND albumTitle = '",albumTitle,"'",sep=""))
  if (nrow(res) > 0)
  {
    warning(paste("Album exists! Overwrite=",overwrite))
    if (overwrite)       ##If overwrite specified, delete all songs and song lines here to start clean.
    {
      ##TODO: Clean out songs and songLines. First query Song to get a list of songs for album. Then delete.
    }
  }else{
    sql <- "INSERT INTO Album (albumNo, albumTitle, artistId) VALUES (<albumNo>,'<albumTitle>',<artistId>)"
    sql <- gsub("<albumNo>",albumNo,sql,fixed = T)
    sql <- gsub("<albumTitle>",albumTitle,sql,fixed = T)
    sql <- gsub("<artistId>",artistId,sql,fixed = T)
    
    dbSendQuery(conn,sql)
    
    ##Get generated album Id
    sql <- paste("SELECT albumId FROM Album WHERE artistId = ",artistId," AND albumTitle = '",albumTitle,"'",sep="")
    res <- dbGetQuery(conn,sql)
    albumId <- res["albumId"]
    
    ##Loop through song lines and add them
    songNo <- 0
    songId <- NULL
    
    #apply(songLines,1,function(x)
    for (i in 1:nrow(songLines))
    {
      x <- songLines[i,]
      if (as.numeric(x["songNo"]) > as.numeric(songNo))
      {
        songNo <- x["songNo"]
        songTitle <- as.character(x["title"])
        
        ##TODO: Insert song into song
        sql <- paste("INSERT INTO Song (songNo, songTitle, albumId) VALUES (",songNo,",'",songTitle,"',",albumId,")",sep="")
        dbSendQuery(conn,sql)
        ##TODO: Get generated songId
        sql <- paste("SELECT songId FROM Song WHERE albumId=",albumId," AND songTitle='",songTitle,"'",sep="")
        res <- dbGetQuery(conn,sql)
        songId <- res["songId"]
        
       }
      
      line = as.character(x["line"])
      
      ##TODO: Insert song line
      sql <- paste("INSERT INTO SongLine (line, lineNo, songId) VALUES ('",line,"',",x["lineNo"],",",songId,")",sep="")
      dbSendQuery(conn,sql)
      
    }
    #)
  }
  dbDisconnect(conn)  
}


######
aUrl <- "/lyrics/devintownsend/oceanmachine.html"
sLines <- getLyricsForAlbum(paste(rootURL,aUrl,sep=""))
artistName <- "Devin Townsend"
songLines <- sLines$songLines
albumNo <- 2
albumTitle = "Ocean Machine"
