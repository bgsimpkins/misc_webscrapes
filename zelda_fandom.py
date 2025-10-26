import sys
import requests
from lxml import html
import pandas as pd

file_out = "/home/bsimpkins/Desktop/BOTW_catalog.xlsx"

def parse_url(url):
    resp = requests.get(url)

    print(f"response={resp}")

    if resp.status_code == 200:
        # print(resp.text)
        tree = html.fromstring(resp.text)
    else:
        print(f"Exiting because you're lame")
        sys.exit()

    return tree


# main = tree.xpath('//div[@class="main-container"]')
# content = main[0].xpath('//div[@id="content"]')

#### Weapons
tree = parse_url("https://zelda.fandom.com/wiki/Weapon")
t = tree[0].xpath('//table[@class="wikitable"]')
rows = t[0].xpath("//tr")

weapons_dict = {
    "weapon":[],
    "compendium_no":[],
    "archetype":[],
    "category":[],
    "shield_simultaneous":[],
    "attack":[],
    "durability":[],
    "description":[]

}


def add_cell_to_weapons_dict(td_i, val):
    if td_i == 0:
        weapons_dict["weapon"].append(val)
    elif td_i == 1:
        weapons_dict["compendium_no"].append(val)
    elif td_i == 2:
        weapons_dict["archetype"].append(val)
    elif td_i == 3:
        weapons_dict["category"].append(val)
    elif td_i == 4:
        weapons_dict["shield_simultaneous"].append(val)
    elif td_i == 5:
        weapons_dict["attack"].append(val)
    elif td_i == 6:
        weapons_dict["durability"].append(val)
    elif td_i == 7:
        weapons_dict["description"].append(val)


i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == len(weapons_dict):
        td_i = 0
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_weapons_dict(td_i,td.text_content().replace("\n",""))

            td_i += 1
    i += 1

weapons_df = pd.DataFrame(weapons_dict)
#weapons_df.to_excel(file_out,index=False,sheet_name="Weapons")

#### Shields
tree = parse_url("https://zelda.fandom.com/wiki/Shield")
botw_header = tree.xpath('//span[@id="Breath_of_the_Wild"]')[0].getparent()

node = botw_header

iter_count = 0
while iter_count <= 20:
    node = node.getnext()
    print(f'node tag={node.tag}')
    if node.tag == "table":
        break
    iter_count += 1

# t = node.xpath('//table[@class="wikitable"]')
# shields_title = tree.xpath('//span[@id="List_of_Shields"]')
# h = shields_title[0].getparent()
# t = h.xpath('//table[@class="wikitable"]')

rows = node[0].findall('tr')

shields_dict = {
    "shield":[],
    "compendium_no":[],
    "shield_guard":[],
    "durability":[],
    "composition":[],
    "description":[]

}


def add_cell_to_shields_dict(td_i, val):
    if td_i == 0:
        shields_dict["shield"].append(val)
    elif td_i == 1:
        shields_dict["compendium_no"].append(val)
    elif td_i == 2:
        shields_dict["shield_guard"].append(val)
    elif td_i == 3:
        shields_dict["durability"].append(val)
    elif td_i == 4:
        shields_dict["composition"].append(val)
    elif td_i == 5:
        shields_dict["description"].append(val)


i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == len(shields_dict):
        td_i = 0
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_shields_dict(td_i,td.text_content().replace("\n",""))

            td_i += 1
    i += 1

shields_df = pd.DataFrame(shields_dict)
#shields_df.to_excel(file_out,index=False,sheet_name="Shields")

with pd.ExcelWriter(file_out) as writer:
    weapons_df.to_excel(writer, sheet_name='Weapons',index=False)
    shields_df.to_excel(writer, sheet_name='Shields',index=False)

