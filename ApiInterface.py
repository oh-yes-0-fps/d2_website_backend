from dataclasses import dataclass, field
import json
import requests
from Enums import AmmoType, StatHashes, sockets
from util.DamageCalc import BuffPackage
from typing import Optional, Tuple
from Enums import WeaponType, WeaponSlot, DamageType
from loadedDatabases import *

@dataclass()
class FiringConfig:
    """for full auto set size to 1 and duration to 0"""
    burstDelay: float
    burstDuration: float
    burstSize: int
    oneAmmoBurst: bool = field(default=False)
    isCharge: bool = field(default=False)


@dataclass()
class FrameData:
    """Class used solely for initializing weapons"""
    frameName: str
    weaponType: WeaponType
    baseDamage: float
    critMult: float
    rangeData: Optional[dict[str, float]]
    reloadData: Optional[dict[str, float]]
    handlingData: Optional[dict[str, float]]
    damageModifiers: BuffPackage
    firingSettings: FiringConfig


@dataclass(frozen=True)
class APIWeaponData:
    """Class used for storing data from the API"""
    name: str
    weaponTypeEnum: int
    intrinsicHash: int
    stats: dict[StatHashes, int]
    statLayout: dict
    perks: dict[int, list[Tuple[int, bool]]]
    image: dict[str, str]

    slot: WeaponSlot
    damageType: DamageType
    ammoType: AmmoType

    def getFrameData(self) -> FrameData:
        with open(".\\database\\weapon_formulas.json") as f:
            jdata = json.load(f)
        weaponTypeID = self.weaponTypeEnum
        weaponFrameHash = self.intrinsicHash
        weaponTypeStr: str = jdata["INDEX"][str(weaponTypeID)]
        itemData: dict = jdata[weaponTypeStr][str(weaponFrameHash)]
        categoryData = jdata[weaponTypeStr]["category"][itemData["category"]]
        archetypeData = jdata[weaponTypeStr]["archetype"][itemData["archetype"]]
        # ------------------------------------------------------------------------
        return FrameData(
            frameName=itemData["name"],
            weaponType=WeaponType.getEnumFromHash(weaponTypeID),
            baseDamage=archetypeData["damage"],
            critMult=archetypeData["critMult"],
            rangeData=categoryData["range"],
            reloadData=categoryData["reload"],
            handlingData=categoryData["handling"],
            damageModifiers=BuffPackage(
                PVP=[],
                PVE=[itemData["pveMult"]],
                MINOR=[categoryData["pveScale"]["minor"]],
                ELITE=[categoryData["pveScale"]["elite"]],
                MINIBOSS=[categoryData["pveScale"]["miniboss"]],
                BOSS=[categoryData["pveScale"]["boss"]],
                VEHICLE=[categoryData["pveScale"]["vehicle"]],
            ),
            firingSettings=FiringConfig(
                burstDelay=archetypeData["burstDelay"],
                burstDuration=archetypeData["burstDuration"],
                burstSize=archetypeData["burstSize"],
                oneAmmoBurst=archetypeData.get("oneAmmoBurst", False),
                isCharge=False,  # TODO
            )
        )


API_ROOT = "https://www.bungie.net/Platform/Destiny2/"
CONTENT_ROOT = "https://www.bungie.net"
WANTED_ENTITIES = []
API_KEY = "89c9db2c0a8b46449bb5e654b6e594d0"  # no yoinky😡
API_KEY_HEADER = {"X-API-Key": API_KEY}


def getManifest():
    manifest = requests.get(API_ROOT + "Manifest/",
                            headers=API_KEY_HEADER).json()
    return manifest


def getEntityDefinition(_entityType: str, _entityHash: int):
    """Only use for niche things that arent in db"""
    entityDef = requests.get(
        API_ROOT + f"Manifest/{_entityType}/{_entityHash}/", headers=API_KEY_HEADER).json()
    return entityDef

def getWeaponDefinition(_weaponHash: int):
    return WEAPONS[str(_weaponHash)]

def getStatLayout(_statLayoutHash: int):
    return STAT_LAYOUTS[str(_statLayoutHash)]

def getPlugSet(_plugSetHash: int):
    return PLUGSETS[str(_plugSetHash)]

def isWeapon(_entityHash: int) -> bool:
    if str(_entityHash) in WEAPONS:
        return True
    else:
        return False


def searchForItems(_searchTerm: str, page: int = 0):
    searchResults = requests.get(
        API_ROOT +
        f"Armory/Search/DestinyInventoryItemDefinition/{_searchTerm}/?page={page}",
        headers=API_KEY_HEADER).json()
    return searchResults


def listOutSearchJson(_searchResults: dict) -> list:
    searchResults = _searchResults
    outLst = []
    while True:
        for item in searchResults["Response"]["results"]["results"]:
            if isWeapon(item["hash"]):
                outLst.append(item["displayProperties"]["name"])
        if searchResults["Response"]["results"]["hasMore"] == False:
            break
        else:
            searchResults = searchForItems(
                "hard", page=_searchResults["Response"]["results"]["page"]+1)
    return outLst

def getItemFromSearchJson(_searchResults: dict, _item: str) -> int:
    searchResults = _searchResults
    while True:
        for item in searchResults["Response"]["results"]["results"]:
            if item["displayProperties"]["name"] == _item:
                return item["hash"]
        if searchResults["Response"]["results"]["hasMore"] == False:
            break
        else:
            searchResults = searchForItems(
                "hard", page=_searchResults["Response"]["results"]["page"]+1)
    return 0

def entityDefJsonToWeaponData(_entityDef: dict) -> APIWeaponData:
    wepDef:dict = _entityDef#["Response"]
    name = wepDef["displayProperties"]["name"]  # done
    weaponTypeHash = wepDef["itemSubType"]  # done

    # done
    intrinsicHash = wepDef["sockets"]["socketEntries"][0]["singleInitialItemHash"]

    stats = {}  # done
    for stat in wepDef["stats"]["stats"].keys():
        stat = int(stat)
        enum = StatHashes.hashToEnum(stat)
        if StatHashes.isWeaponStat(enum):
            stats[enum] = wepDef["stats"]["stats"][str(stat)]["value"]
    for stat in wepDef["investmentStats"]:
        if stat["statTypeHash"] == StatHashes.MAGAZINE.value:
            stats[StatHashes.MAGAZINE] = stat["value"]

    statLayout = getStatLayout(wepDef["stats"]["statGroupHash"])["scaledStats"]

    perks = {}  # done?
    for category in wepDef["sockets"]["socketCategories"]:
        if sockets.isWeaponSocket(category["socketCategoryHash"]):
            entries = wepDef["sockets"]["socketEntries"]
            for i in category["socketIndexes"]:
                perkHashes = []
                perkHashes.append((entries[i]["singleInitialItemHash"], True))
                if entries[i]["plugSources"] == 2:
                    randHash = entries[i].get("randomizedPlugSetHash", 0)
                    if randHash:
                        perkHashes.append(getPlugSet(randHash)["reusablePlugItems"])
                elif entries[i]["plugSources"] == 6:
                    perkGroup = getPlugSet(entries[i]["reusablePlugSetHash"])["reusablePlugItems"]
                    perkGroup = [(x["plugItemHash"], x["currentlyCanRoll"])
                                    for x in perkGroup]
                    perkHashes.extend(perkGroup)
                perks[i] = perkHashes
                #WARNING: this is buttcheeks
            break

    image = {  # done
        "icon": wepDef["displayProperties"]["icon"],
        "seasonalWatermark": wepDef.get("iconWatermark",""),
        "screenshot": wepDef["screenshot"],
        "secondaryIcon": wepDef.get("secondaryIcon", "")
    }

    slot = WeaponSlot.getEnumFromHash(wepDef["inventory"]["bucketTypeHash"])
    ammo = AmmoType.getEnumFromHash(wepDef["equippingBlock"]["ammoType"])
    damageType = DamageType.getEnumFromHash(wepDef["defaultDamageType"])
    return APIWeaponData(name, weaponTypeHash, intrinsicHash, stats, statLayout, perks, image, slot, damageType, ammo)


def dictToString(_dataItem: dict) -> str:
    return json.JSONEncoder(indent=4).encode(_dataItem)

#write the entire manifest database to a file
def updateDatabase():
    manifest = getManifest()
    contentPaths = manifest["Response"]["jsonWorldComponentContentPaths"]["en"]
    itemData:dict[int, dict] = requests.get("https://www.bungie.net" + contentPaths["DestinyInventoryItemDefinition"], headers=API_KEY_HEADER).json()

    weaponDct = {}
    perkDct = {}
    armorDct = {}
    otherDct = {}
    indexDct = {}

    MOD_ENUM = 19
    WEAPON_ENUM = 3
    ARMOR_ENUM = 2
    # PATTERN_ENUM = 30

    for key, value in itemData.items():
        key = int(key)
        if value.get("action", {}) != {}:
            del value["action"]
        if value.get("itemType", 0) == WEAPON_ENUM:
            indexDct[key] = "weapon"
            weaponDct[key] = value
        elif value.get("itemType", 0) == MOD_ENUM:
            indexDct[key] = "perk"
            perkDct[key] = value
        elif value.get("itemType", 0) == ARMOR_ENUM:
            if value["inventory"]["tierTypeName"] == "Exotic":# or value["inventory"]["tierTypeName"] == "Legendary"
                    indexDct[key] = "armor"
                    del value["stats"]
                    armorDct[key] = value
        else:
            indexDct[key] = "other"
            otherDct[key] = value

    with open(".\\database\\items\\index.json", "w") as f:
        json.dump(indexDct, f, indent=4)
    with open(".\\database\\items\\weapon.json", "w") as f:
        json.dump(weaponDct, f, indent=4)
    with open(".\\database\\items\\perk.json", "w") as f:
        json.dump(perkDct, f, indent=4)
    with open(".\\database\\items\\other.json", "w") as f:
        json.dump(otherDct, f, indent=4)
    with open(".\\database\\items\\armor.json", "w") as f:
        json.dump(armorDct, f, indent=4)


    statLayouts = requests.get("https://www.bungie.net" + contentPaths["DestinyStatGroupDefinition"], headers=API_KEY_HEADER).json()
    with open(".\\database\\statLayouts.json", "w") as f:
        json.dump(statLayouts, f, indent=4)

    plugSets = requests.get("https://www.bungie.net" + contentPaths["DestinyPlugSetDefinition"], headers=API_KEY_HEADER).json()
    with open(".\\database\\plugSets.json", "w") as f:
        json.dump(plugSets, f, indent=4)

if __name__ == "__main__":
    updateDatabase()


