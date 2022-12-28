from enum import Enum
from typing import Optional

import ApiInterface as api
from Weapons import Weapon
from Enums import EnemyType


class viewModes(Enum):
    search = 1
    searchResults = 2

    weaponStats = 3
    weaponPerks = 4
    weaponDPS = 5
    weaaponTtk = 6

def dpsMagResultToStr(_magValues: list[float]) -> str:
    outStr = ""
    counter = 1
    for mag in _magValues:
        outStr += f"mag {counter}: {round(mag)} dps\n"
        counter += 1
    return outStr

def clearScreen():
    print("\033c", end="")

weapon:Optional[Weapon] = None

currentMode = viewModes.search

hasAskedForDps = False

rawSearchResults = {}
searchResults = []
selectedWeapon = {}
while True:
    print("Welcome to \"D2 Handbook\" demo!")
    print("-"*33)
    if currentMode == viewModes.search:
        ans = input("Search for a weapon: ")
        rawSearchResults = api.searchForItems(ans)
        searchResults = api.listOutSearchJson(rawSearchResults)
        currentMode = viewModes.searchResults
        clearScreen()
    if currentMode == viewModes.searchResults:
        print("Search Results:")
        for i in range(len(searchResults)):
            print(f"{i}: {searchResults[i]}")
        ans = input("Select a weapon: ")
        if ans.isnumeric():
            ans = int(ans)
            selectedName = searchResults[ans]
            selectedHash = api.getItemFromSearchJson(rawSearchResults, selectedName)
            selectedWeapon:dict = api.getWeaponDefinition(selectedHash)
            currentMode = viewModes.weaponStats
            clearScreen()
    if currentMode == viewModes.weaponStats:
        weapon = Weapon(api.entityDefJsonToWeaponData(selectedWeapon))
        rangeDct = weapon.getRange()
        print(
            weapon,
            f"Falloff: {round(rangeDct['hipFalloffStart'],2)}m|{round(rangeDct['falloffStart'],2)}m",
            f"\nReload Time: {round(weapon.reloadTime,2)}s"
            )
        ans = input("new/dps/ttk: ")
        if ans == "dps":
            currentMode = viewModes.weaponDPS
            clearScreen()
        elif ans == "ttk":
            currentMode = viewModes.weaaponTtk
            clearScreen()
        elif ans == "new":
            currentMode = viewModes.search
            clearScreen()
    if currentMode == viewModes.weaaponTtk:
        if weapon:
            print(api.dictToString(weapon.getTtk(6)))
            ans = input("new/dps/back: ")
            if ans == "dps":
                currentMode = viewModes.weaponDPS
                clearScreen()
            elif ans == "new":
                currentMode = viewModes.search
                clearScreen()
            elif ans == "back":
                currentMode = viewModes.weaponStats
                clearScreen()
    if currentMode == viewModes.weaponDPS:
        rpl = input("what's the reccomended light level?")
        if not rpl.isnumeric():
            print("that's not a number! setting to 1350")
            rpl = 1350
        gpl = input("what's the guardian's power level?")
        if not gpl.isnumeric():
            print("that's not a number! setting to 1350")
            gpl = 1590
        enemyType = input("what's the enemy type? (vehicle, boss, miniboss, elite, minor, enclave)")
        if enemyType == "vehicle":
            enemyType = EnemyType.VEHICLE
        elif enemyType == "miniboss":
            enemyType = EnemyType.MINIBOSS
        elif enemyType == "elite":
            enemyType = EnemyType.ELITE
        elif enemyType == "minor":
            enemyType = EnemyType.MINOR
        elif enemyType == "enclave":
            enemyType = EnemyType.ENCLAVE
        else:
            enemyType = EnemyType.BOSS
        if weapon:
            dmg = weapon.getDamage(int(rpl), int(gpl), enemyType)
            print(f"damage: {dmg}")
            print(dpsMagResultToStr(weapon.getDps(dmg)))
            ans = input("new/ttk/back: ")
            if ans == "new":
                currentMode = viewModes.search
                clearScreen()
            elif ans == "ttk":
                currentMode = viewModes.weaaponTtk
                clearScreen()
            elif ans == "back":
                currentMode = viewModes.weaponStats
                clearScreen()


    clearScreen()
