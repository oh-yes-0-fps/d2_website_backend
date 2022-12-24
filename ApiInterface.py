from dataclasses import dataclass, field
import json
import requests
from Enums import AmmoType, StatHashes, sockets
from util.DamageCalc import BuffPackage
from typing import Optional, Tuple
from Enums import WeaponType, WeaponSlot, DamageType


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
                oneAmmoBurst=archetypeData["oneAmmoBurst"],
                isCharge=False,  # TODO
            )
        )


API_ROOT = "https://www.bungie.net/Platform/Destiny2/"
API_KEY = "89c9db2c0a8b46449bb5e654b6e594d0"  # no yoinky😡
API_KEY_HEADER = {"X-API-Key": API_KEY}


def getManifest():
    manifest = requests.get(API_ROOT + "Manifest/",
                            headers=API_KEY_HEADER).json()
    return manifest


def getEntityDefinition(_entityType: str, _entityHash: int):
    entityDef = requests.get(
        API_ROOT + f"Manifest/{_entityType}/{_entityHash}/", headers=API_KEY_HEADER).json()
    return entityDef


def isWeapon(_entityHash: int) -> bool:
    entityDef = getEntityDefinition(
        "DestinyInventoryItemDefinition", _entityHash)
    bucketHash = entityDef["Response"]["inventory"]["bucketTypeHash"]
    if bucketHash == 2465295065 or bucketHash == 1498876634 or bucketHash == 953998645:
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
    response:dict = _entityDef["Response"]
    name = response["displayProperties"]["name"]  # done
    weaponTypeHash = response["itemSubType"]  # done

    # done
    intrinsicHash = response["sockets"]["socketEntries"][0]["singleInitialItemHash"]

    stats = {}  # done
    for stat in response["stats"]["stats"].keys():
        stat = int(stat)
        enum = StatHashes.hashToEnum(stat)
        if StatHashes.isWeaponStat(enum):
            stats[enum] = response["stats"]["stats"][str(stat)]["value"]

    statLayout = getEntityDefinition("DestinyStatGroupDefinition",  # done
                                    response["stats"]["statGroupHash"])["Response"]["scaledStats"]

    perks = {}  # done?
    for category in response["sockets"]["socketCategories"]:
        if sockets.isWeaponSocket(category["socketCategoryHash"]):
            entries = response["sockets"]["socketEntries"]
            for i in category["socketIndexes"]:
                perkHashes = []
                perkHashes.append((entries[i]["singleInitialItemHash"], True))
                if entries[i]["plugSources"] == 2:
                    perkHashes.append(getEntityDefinition("DestinyPlugSetDefinition",
                                                        entries[i]["randomizedPlugSetHash"])["Response"]["reusablePlugItems"])
                elif entries[i]["plugSources"] == 6:
                    perkGroup = getEntityDefinition("DestinyPlugSetDefinition", entries[i]["reusablePlugSetHash"])[
                        "Response"]["reusablePlugItems"]
                    perkGroup = [(x["plugItemHash"], x["currentlyCanRoll"])
                                    for x in perkGroup]
                    perkHashes.extend(perkGroup)
                perks[i] = perkHashes
                #WARNING: this is buttcheeks
            break

    image = {  # done
        "icon": response["displayProperties"]["icon"],
        "seasonalWatermark": response.get("iconWatermark",""),
        "screenshot": response["screenshot"],
        "secondaryIcon": response.get("secondaryIcon", "")
    }

    slot = WeaponSlot.getEnumFromHash(response["inventory"]["bucketTypeHash"])
    ammo = AmmoType.getEnumFromHash(response["equippingBlock"]["ammoType"])
    damageType = DamageType.getEnumFromHash(response["defaultDamageType"])
    return APIWeaponData(name, weaponTypeHash, intrinsicHash, stats, statLayout, perks, image, slot, damageType, ammo)


def dictToString(_dataItem: dict) -> str:
    return json.JSONEncoder(indent=4).encode(_dataItem)
