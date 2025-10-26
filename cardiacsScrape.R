require(XML)
require(RCurl)
require(RMySQL)

setwd("/home/ben/Documents/R/Cardiacs_scrape/")

##Trims leading and trailing whitespace.
trim <- function(x)
{
  
  ##Leading
  x <- gsub("^\\s+","",x)
  
  ##Trailing
  x <- gsub("\\s+$","",x)
  
  x
}

#####Create flat file

albumDirs <- readLines("albums.txt")

theTable <- data.frame()
albumNo <- 1
for (a in albumDirs)
{
  
  html <- getURL(a)
  doc <- htmlParse(html,asText = T)
  songs <- xpathSApply(doc,"//a/@href")
  sDir <- unlist(strsplit(a,"/"))
  album <- sDir[length(sDir)]
  sDir <- paste(sDir[1],"//",paste(sDir[3:(length(sDir)-1)],"/",collapse="",sep=""),sep="")
  print(paste("----",album,sep=""))
  songNo <- 1
  for (s in songs)
  {
    html <- getURL(paste(sDir,s,sep=""))
    doc <- htmlParse(html,asText = T)
    inner <- xpathSApply(doc,"//p//text()")
    title <- xmlValue(inner[[1]])
    title <- gsub(pattern = "\n    ","",title)
    lineNo <- 1
    print(title)
    for (l in inner[2:length(inner)])
    {
      l <- gsub(pattern = "\n    ","",xmlValue(l))
      if (length(grep("Â",l)) == 0){
        theTable <- rbind(theTable,data.frame(albumNo,album,songNo,song=title,lineNo,line=l))
        lineNo <- lineNo + 1
      }
      ##
    }
    songNo <- songNo + 1
  }
  albumNo <- albumNo + 1
}

##can be duplicates...
theTable <- unique(theTable)

#write.csv(theTable,"CardiacsScrapeResult.csv",row.names=F)

##Normalize for SQL DB
albums <- unique(theTable[,c("albumNo","album")])
songs <- unique(theTable[,c("albumNo","songNo","song")])
songLines <- theTable[,c("albumNo","songNo","lineNo","line")]

con <- dbConnect(MySQL(),
                 user="bsimpkins",
                 password="yourmomma",
                 host="127.0.0.1",
                 dbname="lyric_database")

dbWriteTable(con,"t_albums",albums)

sql <- "
  INSERT INTO Artist (artistName, dateFormed, stillTogether, placeOfOrigin)
    VALUES ('Cardiacs', '1977-01-01',1, 'Kingston upon Thames, Greater London')
"
dbSendQuery(con,sql)

artistId <- dbGetQuery(con,"SELECT LAST_INSERT_ID()")

sql <- paste("
  INSERT INTO Album (albumNo, albumTitle, artistId)
    SELECT albumNo, album, " ,artistId, "
    FROM t_albums
",sep="")

dbSendQuery(con,sql)

sql <- paste("
  SELECT 
    albumId,
    albumNo,
    albumTitle
  FROM Album 
  WHERE artistId =
", artistId, sep="")

albums <- dbGetQuery(con,sql)


songs <- merge(albums,songs)

dbWriteTable(con,"t_songs",songs)

##Crapola. Didn't work in 64-bit Linux Mint. Have to do it the old-fashioned way.
#lastId <- fetch(dbSendQuery(con,"SELECT LAST_INSERT_ID(), ROW_COUNT();"))

sql <- "
  INSERT INTO Song (songNo,songTitle,albumId)
    SELECT songNo,song,albumId
    FROM t_songs
"

dbSendQuery(con,sql)

sql <- paste("
  SELECT s.songId, s.songNo, a.albumNo, a.albumId
  FROM Song s
    INNER JOIN Album a
      ON s.albumId = a.albumId
  WHERE a.artistId = ",artistId,sep="")
  
songs <- dbGetQuery(con,sql)

songLines <- merge(songLines,songs)
dbWriteTable(con,"t_songLines",songLines)

sql <- "
  INSERT INTO SongLine (lineNo, line, songId)
    SELECT lineNo,line,songId
    FROM t_songLines
"
dbSendQuery(con,sql)

sql <- "
  DROP TABLE t_albums
"  
dbSendQuery(con,sql)

sql <- "
  DROP TABLE t_songs;
"
dbSendQuery(con,sql)

sql <- "
  DROP TABLE t_songLines;
"
dbSendQuery(con,sql)

dbDisconnect(con)
