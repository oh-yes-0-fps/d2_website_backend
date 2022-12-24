from enum import Enum
import ApiInterface as api
from Weapons import Weapon


class viewModes(Enum):
    search = 1
    searchResults = 2

    weaponStats = 3
    weaponPerks = 4
    weaponDPS = 5


def clearScreen():
    print("\033c", end="")


currentMode = viewModes.search

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
            selectedWeapon = api.getItemFromSearchJson(rawSearchResults, selectedName)
            selectedWeapon = api.getEntityDefinition(
                "DestinyInventoryItemDefinition", selectedWeapon)
            currentMode = viewModes.weaponStats
            clearScreen()
    if currentMode == viewModes.weaponStats:
        weapon = Weapon(api.entityDefJsonToWeaponData(selectedWeapon))
        print(weapon)
        input("Would you like to close the cli?")
        break


    clearScreen()
