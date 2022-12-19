

from math import ceil
from typing import Any, Tuple, Type, Union
from Perks import Perk  # Weapons.
from Enums import WeaponType, IntrinsicFrame
from util.DpsCalc import calcDPS, calcRefund
from util.TtkCalc import calcTtk


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

def rpmToDelay(_rpm: int) -> float:
    """converts rpm to delay"""
    return 60/_rpm


class Weapon:
    """Base class for all weapons"""
    __perks: list[Perk] = []

    def __init__(self, weaponData) -> None:
        self.name = "Base Weapon"

        self.rangeStat = 100
        self.stabilityStat = 100
        self.handlingStat = 100
        self.reloadStat = 100
        self.aimAssistStat = 100
        self.zoomStat = 100
        self.airborneStat = 100
        self.recoilDirStat = 100
        self.rpmStat = 100 #this will immediately be useless once burst delay is initialized
        self.magSize = 10
        self.inventorySizeStat = 100

        self.burstSize = 0
        self.burstDuration = 0.0
        self.burstDelay = rpmToDelay(self.rpmStat)
        # self.chargeTime = 0.0
        self.reloadTime = 1.0

        self.critMult = 1.0


        self.refunds:list[dict[str,Any]] = []


    def configFiring(self, _burstSize: int, _burstDuration: float, _burstDelay: float) -> None:
        """for full auto set size to 1 and duration to 0"""
        self.burstSize = _burstSize
        self.burstDuration = _burstDuration
        self.burstDelay = _burstDelay

    def delPerk(self, _perk: Type[Perk]) -> None:
        for perk in self.__perks:
            if isinstance(perk, _perk):
                perk.remove(self)
                self.__perks.remove(perk)
                return

    def addPerk(self, _perk: Type[Perk]) -> None:
        self.delPerk(_perk)
        try:
            prk = _perk() #type: ignore
        except:
            return
        self.__perks.append(prk)
        prk.apply(self)

    def getReserves(self) -> int:
        #TODO: try and figure out formula for reserves
        return 20

    def getDps(self, _damage: float, _shotsMissed:int = 0, _isChargeTime:bool = False) -> list[float]:
        """calculates the dps of the weapon"""
        return calcDPS(self.burstDelay, _damage, self.critMult, self.reloadTime, self.magSize, self.getReserves(),
                        _isChargeTime, _shotsMissed, self.refunds)

    def graphDPS(self, _damage:float):
        pass

    def getTtk(self, _resilience:int, _damage:float, _critMult:float) -> dict[str, Union[int, float]]:
        return calcTtk(self.burstDelay, _resilience, _damage, _critMult, self.magSize)

    #
    ##from here on its just establishing a perk interface
    #
    @staticmethod
    def modifierConversion(number:float) -> float:
        if number > 0:
            return 1 + number
        if number < 0:
            return 1 / (1 - number)
        return 1.0

    def modCrit(self, _critBuff:float, _additive:bool) -> None:
        if _additive:
            self.critMult += _critBuff
            return
        self.critMult *= self.modifierConversion(_critBuff)

    def modReloadStat(self, _reloadBuff:float, _additive:bool) -> None:
        if _additive:
            self.reloadTime += _reloadBuff
            return
        self.reloadTime *= self.modifierConversion(_reloadBuff)

    def modMagSize(self, _magBuff:int, _additive:bool) -> None:
        if _additive:
            self.magSize += _magBuff
            return
        self.magSize *= self.modifierConversion(_magBuff)

    def modRefund(self, _refund:dict[str,Any]) -> None:
        self.refunds.append(_refund)

    def modChargeTime(self, _chargeTime:float, _additive:bool) -> None:
        if _additive:
            self.burstDelay += _chargeTime
            return
        self.burstDelay *= self.modifierConversion(_chargeTime)

    def modFireRate(self, _burstDelay:float) -> None:
        """always multiplicative"""
        self.burstDelay *= self.modifierConversion(_burstDelay)

    def modRange(self, _rangeBuff:float, _additive:bool) -> None:
        if _additive:
            self.rangeStat += _rangeBuff
            return
        self.rangeStat *= self.modifierConversion(_rangeBuff)

    def modStability(self, _stabilityBuff:float, _additive:bool) -> None:
        if _additive:
            self.stabilityStat += _stabilityBuff
            return
        self.stabilityStat *= self.modifierConversion(_stabilityBuff)

    def modHandling(self, _handlingBuff:float, _additive:bool) -> None:
        if _additive:
            self.handlingStat += _handlingBuff
            return
        self.handlingStat *= self.modifierConversion(_handlingBuff)

    def modAimAssist(self, _aimAssistBuff:float, _additive:bool) -> None:
        if _additive:
            self.aimAssistStat += _aimAssistBuff
            return
        self.aimAssistStat *= self.modifierConversion(_aimAssistBuff)

    def modZoom(self, _zoomBuff:float, _additive:bool) -> None:
        if _additive:
            self.zoomStat += _zoomBuff
            return
        self.zoomStat *= self.modifierConversion(_zoomBuff)

    def modAirborne(self, _airborneBuff:float, _additive:bool) -> None:
        if _additive:
            self.airborneStat += _airborneBuff
            return
        self.airborneStat *= self.modifierConversion(_airborneBuff)

    def modRecoilDir(self, _recoilDirBuff:float, _additive:bool) -> None:
        if _additive:
            self.recoilDirStat += _recoilDirBuff
            return
        self.recoilDirStat *= self.modifierConversion(_recoilDirBuff)

    def modInventorySize(self, _inventorySizeBuff:float, _additive:bool) -> None:
        if _additive:
            self.inventorySizeStat += _inventorySizeBuff
            return
        self.inventorySizeStat *= self.modifierConversion(_inventorySizeBuff)

