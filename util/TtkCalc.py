from math import ceil
from typing import Union


RESILIENCE_VALUES = {
    0: 115 + 70.01,# 185.01
    1: 116 + 70.01,# 186.01
    2: 117 + 70.01,# 187.01
    3: 118 + 70.01,# 188.01
    4: 119 + 70.01,# 189.01
    5: 120 + 70.01,# 190.01
    6: 122 + 70.01,# 192.01
    7: 124 + 70.01,# 194.01
    8: 126 + 70.01,# 196.01
    9: 128 + 70.01,# 198.01
    10:130 + 70.01 # 200.01
}


def calcTtk(_shotDelay:float, _resilience:int, _damage:float, _critMult:float, _magSize:int) -> dict[str, Union[int, float]]:
    critDmg = _damage*_critMult
    dmg = _damage
    health = RESILIENCE_VALUES[_resilience]

    outDict = {
        "ShotsNeeded": 0,
        "Optimal TtK": 0.0,
        "Crit Percent": 0.0,
        "Bodyshot Ttk": 0.0
    }

    if _critMult == 0.0: #Like for explosive type weapons
        #val is shots needed after initial shot
        val = ceil((health-dmg)/(dmg))
        outDict["ShotsNeeded"] = ceil((health-dmg)/(dmg)) + 1
        outDict["Optimal TtK"] = ceil((health-dmg)/(dmg))*_shotDelay
        outDict["Crit Percent"] = 0.0
        outDict["Bodyshot Ttk"] = ceil((health-dmg)/(dmg))*_shotDelay
        return outDict

    if _magSize*_damage < health:
        #TODO: maybe add option for ttk including reloads?, like a gl ttk
        return outDict

    lShotsNeeded = ceil((health-critDmg)/(critDmg)) + 1
    outDict["ShotsNeeded"] = lShotsNeeded
    outDict["Optimal TtK"] = (lShotsNeeded-1)*_shotDelay
    outDict["Crit Percent"] = round((ceil((health - (lShotsNeeded*dmg)) / (critDmg-dmg)) / lShotsNeeded), 2)
    outDict["Bodyshot Ttk"] = ceil((health-dmg)/(dmg))*_shotDelay
    return outDict