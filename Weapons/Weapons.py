

from typing import Any, Tuple
from Weapons.Perks import Perk  # Weapons.
from Weapons.Enums import WeaponType, IntrinsicFrame

__weaponMapping = {
    WeaponType.SIDEARM: {
        IntrinsicFrame.PRECISION: None,
        IntrinsicFrame.ADDAPTIVE_BURST: None,
        IntrinsicFrame.AGGRESSIVE_BURST: None,
        IntrinsicFrame.ADAPTIVE: None
    }
}

def rpmToDelay(_rpm: int) -> float:
    """converts rpm to delay"""
    return 60/_rpm


class Weapon:

    __parts = {}
    __perks: list[Perk] = []

    @staticmethod
    def getNeededInstance(_weaponType: WeaponType, _weaponFrame: IntrinsicFrame) -> Any:
        pass

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
        dps = (mag * _damage) / timeToEmpty

    def graphDPS(self, _damage:float):
        #TODO:
        #This will be very performance intensive, meant more for content creators.
        #Cuz its a website should i use plotly? not sure prob matplotlib for now
        pass
