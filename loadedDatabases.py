import json

ITEMS = {}
WEAPONS = {}
PERKS = {}
ARMOR = {}
PLUGSETS = {}
STAT_LAYOUTS = {}
#This uses around 150mb of ram but allows for faster loading times

with open(".\\database\\items\\index.json", "r") as f:
    ITEMS:dict = json.load(f)
with open(".\\database\\items\\weapon.json", "r") as f:
    WEAPONS:dict = json.load(f)
with open(".\\database\\items\\perk.json", "r") as f:
    PERKS:dict = json.load(f)
with open(".\\database\\items\\armor.json", "r") as f:
    ARMOR:dict = json.load(f)
with open(".\\database\\plugSets.json", "r") as f:
    PLUGSETS:dict = json.load(f)
with open(".\\database\\statLayouts.json", "r") as f:
    STAT_LAYOUTS:dict = json.load(f)
