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
t = tree.xpath('//table[contains(@class, "wikitable")]')
rows = t[0].xpath("//tr")

item_dict = {
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
        item_dict["weapon"].append(val)
    elif td_i == 1:
        item_dict["compendium_no"].append(val)
    elif td_i == 2:
        item_dict["archetype"].append(val)
    elif td_i == 3:
        item_dict["category"].append(val)
    elif td_i == 4:
        item_dict["shield_simultaneous"].append(val)
    elif td_i == 5:
        item_dict["attack"].append(val)
    elif td_i == 6:
        item_dict["durability"].append(val)
    elif td_i == 7:
        item_dict["description"].append(val)


i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == len(item_dict):
        td_i = 0
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_weapons_dict(td_i,td.text_content().replace("\n",""))

            td_i += 1
    i += 1

weapons_df = pd.DataFrame(item_dict)
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

item_dict = {
    "shield":[],
    "compendium_no":[],
    "shield_guard":[],
    "durability":[],
    "composition":[],
    "description":[]

}


def add_cell_to_shields_dict(td_i, val):
    if td_i == 0:
        item_dict["shield"].append(val)
    elif td_i == 1:
        item_dict["compendium_no"].append(val)
    elif td_i == 2:
        item_dict["shield_guard"].append(val)
    elif td_i == 3:
        item_dict["durability"].append(val)
    elif td_i == 4:
        item_dict["composition"].append(val)
    elif td_i == 5:
        item_dict["description"].append(val)


i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == len(item_dict):
        td_i = 0
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_shields_dict(td_i,td.text_content().replace("\n",""))

            td_i += 1
    i += 1

shields_df = pd.DataFrame(item_dict)
#shields_df.to_excel(file_out,index=False,sheet_name="Shields")

#### Bows
tree = parse_url("https://zelda.fandom.com/wiki/Bow")
botw_header = tree.xpath('//span[@id="Breath_of_the_Wild"]')[0].getparent()

node = botw_header

iter_count = 0
while iter_count <= 20:
    node = node.getnext()
    print(f'node tag={node.tag}')
    if node.tag == "table":
        break
    iter_count += 1

rows = node[0].findall('tr')

item_dict = {
    "bow": [],
    "compendium_no": [],
    "strength": [],
    "durability": [],
    "range": [],
    "description": []

}


def add_cell_to_bows_dict(td_i, val):
    if td_i == 0:
        item_dict["bow"].append(val)
    elif td_i == 1:
        item_dict["compendium_no"].append(val)
    elif td_i == 2:
        item_dict["strength"].append(val)
    elif td_i == 3:
        item_dict["durability"].append(val)
    elif td_i == 4:
        item_dict["range"].append(val)
    elif td_i == 5:
        item_dict["description"].append(val)

i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == len(item_dict):
        td_i = 0
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_bows_dict(td_i,td.text_content().replace("\n",""))

            td_i += 1
    i += 1

bows_df = pd.DataFrame(item_dict)

#### Armor
tree = parse_url("https://zelda.fandom.com/wiki/Armor/Breath_of_the_Wild")

t = tree.xpath('//table[contains(@class, "wikitable")]')

## Three tables. Head gear, body gear, leg gear. Create category to distinguish

item_dict = {
    "armor": [],
    "category": [],
    "defense": [],
    "effect": [],
    "description": []
}


def add_cell_to_armour_dict(td_i, val):
    if td_i == 0:
        item_dict["armor"].append(val)
    elif td_i == 1:
        item_dict["defense"].append(val)
    elif td_i == 2:
        item_dict["effect"].append(val)
    elif td_i == 3:
        item_dict["description"].append(val)


# Head gear
rows = t[0].xpath("//tr")

i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == 4:
        td_i = 0
        item_dict["category"].append('Head Gear')
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_armour_dict(td_i, td.text_content().replace("\n",""))

            td_i += 1
    i += 1

# Body gear
rows = t[1].xpath("//tr")

i = 1  # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == 4:
        td_i = 0
        item_dict["category"].append('Body Gear')
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_armour_dict(td_i, td.text_content().replace("\n", ""))

            td_i += 1
    i += 1

# Leg gear
rows = t[2].xpath("//tr")

i = 1  # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == 4:
        td_i = 0
        item_dict["category"].append('Leg Gear')
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_armour_dict(td_i, td.text_content().replace("\n", ""))

            td_i += 1
    i += 1


armour_df = pd.DataFrame(item_dict)

#### Materials
tree = parse_url("https://zelda.fandom.com/wiki/Material/Breath_of_the_Wild")
t = tree.xpath('//table[contains(@class, "wikitable")]')

item_dict = {
    "material": [],
    "description": [],
    "value": [],
    "additional_uses": []
}


def add_cell_to_mats_dict(td_i, val):
    if td_i == 0:
        item_dict["material"].append(val)
    elif td_i == 1:
        item_dict["description"].append(val)
    elif td_i == 2:
        item_dict["value"].append(val)
    elif td_i == 3:
        item_dict["additional_uses"].append(val)


rows = t[0].xpath("//tr")

i = 1 # Skip header row

# Loop through rows
while i < len(rows):
    tds = rows[i].getchildren()
    # Loop through cells

    if len(tds) == 4:
        td_i = 0
        for td in tds:
            print(f"cell #{td_i}: {td.text_content()}")
            add_cell_to_mats_dict(td_i, td.text_content().replace("\n",""))

            td_i += 1
    i += 1

materials_df = pd.DataFrame(item_dict)


#################### Write Excel file
with pd.ExcelWriter(file_out) as writer:
    weapons_df.to_excel(writer, sheet_name='Weapons', index=False)
    shields_df.to_excel(writer, sheet_name='Shields', index=False)
    bows_df.to_excel(writer, sheet_name='Bows', index=False)
    armour_df.to_excel(writer, sheet_name='Armour', index=False)
    materials_df.to_excel(writer, sheet_name='Materials', index=False)

