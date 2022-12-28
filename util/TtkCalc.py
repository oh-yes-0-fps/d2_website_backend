from math import ceil
from typing import Union
from ApiInterface import FiringConfig


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

def extraBurstBullets(_hitsNeeded:int, _burstSize:int) -> int:
    return (_hitsNeeded%_burstSize)-1 if _hitsNeeded%_burstSize > 0 else 0

def critPercent(_health:float, _hitsNeeded:int, _dmg:float, _critMult:float) -> float:
    if _critMult <= 1:
        return 0
    return round((ceil((_health - (_hitsNeeded*_dmg)) / ((_dmg*_critMult)-_dmg)) / _hitsNeeded), 2)

def calcTtk(_firingData:FiringConfig, _resilience:int, _damage:float, _critMult:float, _magSize:int) -> dict[str, Union[int, float]]:
    #YES, i could make this code smaller but it would be most likely slower(needing a for loop) and more prone to bugs
    outDict = {#the "schema" for the output
        "Ammo_Needed": 0,
        "Hits_Needed": 0,
        "Optimal_TtK": 0.0,
        "Crit_Percent": 0.0,
        "Bodyshot_Ttk": 0.0
    }

    critDmg = _damage*_critMult
    dmg = _damage
    health = RESILIENCE_VALUES[_resilience]

    burstDelay = _firingData.burstDelay
    burstSize = _firingData.burstSize
    burstDuration = _firingData.burstDuration

    dmgPerAmmo = dmg*burstSize if _firingData.oneAmmoBurst else dmg

    #for some weapons like gl where a whole mag won't kill
    if _magSize*dmgPerAmmo < health:
        return outDict
    #-------------------------------------------------------------------
    #Theres 4 categoris of firing,
    #Standard: 1 bullet and ammo per shot, no duration
    #Scatter: many bullets but 1 ammo per shot, no duration
    #Pulse: many bullet and ammo per shot, has duration
    #Fusion: many bullets but 1 ammo per shot, has duration

    #pulse and fusion can be handled the same way
    if burstSize > 1 and burstDuration > 0:
        hitsNeeded = ceil(health/critDmg)
        ammoNeeded = ceil(hitsNeeded/burstSize) if _firingData.oneAmmoBurst else hitsNeeded
        outDict["Ammo_Needed"] = ammoNeeded
        outDict["Hits_Needed"] = hitsNeeded
        interBurstDelay = burstDuration/(burstSize-1)
        burstsNeeded = ceil(hitsNeeded/burstSize)
        outDict["Optimal_TtK"] = (((burstsNeeded-1)*burstDelay + burstsNeeded*burstDuration) + 
                                    extraBurstBullets(hitsNeeded, burstSize)*interBurstDelay)
        bodyHitsNeeded = ceil(health/dmg)
        bodyBurstsNeeded = ceil(bodyHitsNeeded/burstSize)
        outDict["Bodyshot_Ttk"] = (((bodyBurstsNeeded-1)*burstDelay + bodyBurstsNeeded*burstDuration) +
                                    extraBurstBullets(bodyHitsNeeded, burstSize)*interBurstDelay)
        outDict["Crit_Percent"] = critPercent(health, hitsNeeded, dmg, _critMult)

    #this can handle standard
    elif burstSize == 1 and burstDuration == 0:
        hitsNeeded = ceil(health/critDmg)
        outDict["Ammo_Needed"] = hitsNeeded
        outDict["Hits_Needed"] = hitsNeeded
        outDict["Optimal_TtK"] = (hitsNeeded-1)*burstDelay
        outDict["Bodyshot_Ttk"] = ceil(health/dmg)*burstDelay-burstDelay
        outDict["Crit_Percent"] = critPercent(health, hitsNeeded, dmg, _critMult)

    #this can handle scatter
    elif burstSize > 1 and burstDuration == 0:
        hitsNeeded = ceil(health/critDmg)
        ammoNeeded = ceil(hitsNeeded/burstSize) if _firingData.oneAmmoBurst else hitsNeeded
        #                                          ^^^^^^^^^^^^^^^^^^^^^^^^ should always be true
        outDict["Ammo_Needed"] = ammoNeeded
        outDict["Hits_Needed"] = hitsNeeded
        outDict["Optimal_TtK"] = (ceil(hitsNeeded/burstSize)-1)*burstDelay
        outDict["Bodyshot_Ttk"] = ceil(ceil(health/dmg)/burstSize)*burstDelay-burstDelay
        outDict["Crit_Percent"] = critPercent(health, hitsNeeded, dmg, _critMult)


    outDict["Optimal_TtK"] = round(outDict["Optimal_TtK"], 2)
    outDict["Bodyshot_Ttk"] = round(outDict["Bodyshot_Ttk"], 2)
    return outDict