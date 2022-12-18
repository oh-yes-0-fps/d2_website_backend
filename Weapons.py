

from math import ceil
from typing import Any, Tuple, Union
from Perks import Perk  # Weapons.
from Enums import WeaponType, IntrinsicFrame

# __weaponMapping = {
#     WeaponType.SIDEARM: {
#         IntrinsicFrame.PRECISION: None,
#         IntrinsicFrame.ADDAPTIVE_BURST: None,
#         IntrinsicFrame.AGGRESSIVE_BURST: None,
#         IntrinsicFrame.ADAPTIVE: None
#     }
# }

resilienceValues = {
    #TODO: get actual values
    0: 184,
    1: 186,
    2: 188,
    3: 190,
    4: 192,
    5: 194,
    6: 196,
    7: 198,
    8: 200,
    9: 202,
    10:204
}

def rpmToDelay(_rpm: int) -> float:
    """converts rpm to delay"""
    return 60/_rpm


class Weapon:

    __parts = {}
    __perks: list[Perk] = []

    def __init__(self) -> None:
        self.burstSize = 0
        self.burstDuration = 0.0
        self.burstDelay = 0.0
        self.chargeTime = 0.0

        self.magSize = 0

        self.refunds:list[dict[str,int]] = []

    def configFiring(self, _burstSize: int, _burstDuration: float, _burstDelay: float) -> None:
        """for full auto set size to 1 and duration to 0"""
        self.burstSize = _burstSize
        self.burstDuration = _burstDuration
        self.burstDelay = _burstDelay

    def calcReserves(self) -> int:
        pass

    def calcRefund(self, _magSize:int, _shotsMissed:int) -> None:
        """This is by far the slowest thing here with requiring a while loop,
        I could just have static formula for existing perks but thats cringe"""
        if len(self.refunds) == 0:
            return _magSize
        currMag = _magSize
        shotsFired = 0
        while currMag:
            isCrit = True
            if shotsFired < _shotsMissed:
                isCrit = False
            for refund in self.refunds: #💀python loops
                if refund["CRIT"] == isCrit:
                    req = refund["REQUIREMENT"]
                    if shotsFired/req == int(shotsFired/req):
                        currMag += refund["REFUND"]
            shotsFired += 1
            currMag -= 1
        return shotsFired



    def calcDPS(self, _damage: float, _shotsMissed:int) -> list[float]:
        """calculates the dps of the weapon"""
        timeToFire = self.burstDuration + self.burstDelay# + self.chargeTime
        mag = self.calcRefund(self.magSize, _shotsMissed)
        timeToEmpty = timeToFire * mag-1
        damagePerMag = (mag * _damage)
        dps = damagePerMag / timeToEmpty

    def graphDPS(self, _damage:float):
        
        pass

    def ttk(self, _resilience:int, _damage:float, _critMult:float) -> dict[str, Union[int, float]]:
        critDmg = _damage*_critMult
        dmg = _damage
        health = resilienceValues[_resilience]
        shootDelay = self.burstDelay

        outDict = {
            "ShotsNeeded": 0,
            "Optimal TtK": 0.0,
            "Crit Percent": 0.0,
            "Bodyshot Ttk": 0.0
        }

        if _critMult == 0: #Like for explosive type weapons
            #val is shots needed after initial shot
            val = ceil((health-dmg)/(dmg))
            outDict["ShotsNeeded"] = ceil((health-dmg)/(dmg)) + 1
            outDict["Optimal TtK"] = ceil((health-dmg)/(dmg))*shootDelay
            outDict["Crit Percent"] = 0.0
            outDict["Bodyshot Ttk"] = ceil((health-dmg)/(dmg))*shootDelay
            return outDict

        if self.magSize*_damage < health:
            #TODO: maybe add option for ttk including reloads?, like a gl ttk
            return outDict

        lShotsNeeded = ceil((health-critDmg)/(critDmg)) + 1
        outDict["ShotsNeeded"] = lShotsNeeded
        outDict["Optimal TtK"] = (lShotsNeeded-1)*shootDelay
        outDict["Crit Percent"] = round((ceil((health - (lShotsNeeded*dmg)) / (critDmg-dmg)) / lShotsNeeded), 2)
        outDict["Bodyshot Ttk"] = ceil((health-dmg)/(dmg))*shootDelay
