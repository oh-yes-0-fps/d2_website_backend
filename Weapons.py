

from dataclasses import dataclass, field
from math import ceil
from typing import Any, Optional, Tuple, Type, Union
# from perks.Perks import Perk, PerkSlider, PerkToggle  # Weapons.
from Enums import AmmoType, DamageType, WeaponSlot, WeaponType, StatHashes
from util.DpsCalc import calcDPS, calcRefund
from util.TtkCalc import calcTtk
from util.StatCalc import calcReload, calcHandling, calcRange
from util.DamageCalc import calcDmgPve, BuffPackage
from ApiInterface import APIWeaponData, FiringConfig, FrameData


RESILIENCE_VALUES = {
    0: 115 + 70.01,  # 185.01
    1: 116 + 70.01,  # 186.01
    2: 117 + 70.01,  # 187.01
    3: 118 + 70.01,  # 188.01
    4: 119 + 70.01,  # 189.01
    5: 120 + 70.01,  # 190.01
    6: 122 + 70.01,  # 192.01
    7: 124 + 70.01,  # 194.01
    8: 126 + 70.01,  # 196.01
    9: 128 + 70.01,  # 198.01
    10: 130 + 70.01  # 200.01
}


def rpmToDelay(_rpm: int) -> float:
    """converts rpm to delay"""
    return 60/_rpm


class Stat:
    def __init__(self, _baseValue: int):
        self.baseValue: int = _baseValue
        self.modValues: list[int] = []
        self.associatedScalar: float = 1.0

    def __bool__(self) -> bool:
        return self.baseValue >= 0

    def sumOfMods(self) -> int:
        return sum(self.modValues)

    def val(self) -> int:
        """DOES NOT TAKE INTO ACCOUNT SCALARS"""
        return self.baseValue + self.sumOfMods()


class Weapon:
    """Base class for all weapons"""
    # __perks: list[Perk] = []

    UI_Sliders = []
    UI_Toggles = []

    def __init__(self, _weaponData: APIWeaponData) -> None:

        self.weaponData = _weaponData
        l_weaponStats = self.weaponData.stats
        self.weaponFrame = self.weaponData.getFrameData()

        self.name = _weaponData.name

        self.impactStat = Stat(l_weaponStats.get(StatHashes.IMPACT, -1))
        self.rangeStat = Stat(l_weaponStats.get(StatHashes.RANGE, -1))
        self.stabilityStat = Stat(l_weaponStats.get(StatHashes.STABILITY, -1))
        self.handlingStat = Stat(l_weaponStats.get(StatHashes.HANDLING, -1))
        self.reloadStat = Stat(l_weaponStats.get(StatHashes.RELOAD, -1))
        self.aimAssistStat = Stat(l_weaponStats.get(StatHashes.AIMASSIST, -1))
        self.zoomStat = Stat(l_weaponStats.get(StatHashes.ZOOM, -1))
        self.airborneStat = Stat(l_weaponStats.get(StatHashes.AIRBORNE, -1))
        self.recoil_dirStat = Stat(l_weaponStats.get(StatHashes.RECOIL_DIR, -1))
        self.rpmStat = Stat(l_weaponStats.get(StatHashes.RPM, -1))
        self.magazineStat = Stat(l_weaponStats.get(StatHashes.MAGAZINE, -1))
        self.inventory_sizeStat = Stat(l_weaponStats.get(StatHashes.INVENTORY_SIZE, -1))
        self.velocityStat = Stat(l_weaponStats.get(StatHashes.VELOCITY, -1))
        self.blast_radiusStat = Stat(l_weaponStats.get(StatHashes.BLAST_RADIUS, -1))
        self.draw_timeStat = Stat(l_weaponStats.get(StatHashes.DRAW_TIME, -1))
        self.swing_speedStat = Stat(l_weaponStats.get(StatHashes.SWING_SPEED, -1))
        self.charge_timeStat = Stat(l_weaponStats.get(StatHashes.CHARGE_TIME, -1))
        self.guard_efficiencyStat = Stat(l_weaponStats.get(StatHashes.GUARD_EFFICIENCY, -1))
        self.guard_enduranceStat = Stat(l_weaponStats.get(StatHashes.GUARD_ENDURANCE, -1))
        self.guard_resistanceStat = Stat(l_weaponStats.get(StatHashes.GUARD_RESISTANCE, -1))
        self.charge_rateStat = Stat(l_weaponStats.get(StatHashes.CHARGE_RATE, -1))
        self.shield_durationStat = Stat(l_weaponStats.get(StatHashes.SHIELD_DURATION, -1))

        self.baseDamage = self.weaponFrame.baseDamage
        self.critMult = self.weaponFrame.critMult

        self.firingSettings = self.weaponFrame.firingSettings

        # these are for multiplicative buffs
        self.hipFireRangeScalar = 1.0  # only one not integrated
        # now integrated into the stats
        # reloadDurationScalar, integrated with reload
        # swapDurationScalar, integrated with handling
        # aimAssistScalar, integrated with aim assist
        # rangeScalar, integrated with range
        # fireRateScalar, integrated with fire rate

        self.refunds: list[dict[str, Any]] = []
        self.damageScalars = self.weaponFrame.damageModifiers

        self.weaponType: WeaponType = self.weaponFrame.weaponType
        self.ammoType: AmmoType = self.weaponData.ammoType
        self.damageType: DamageType = self.weaponData.damageType
        self.weaponSlot: WeaponSlot = self.weaponData.slot

    def getStatAttrFromHash(self, _statHash: int) -> Stat:
        """returns the stat attribute from the hash"""
        """This is the most scuffed thing ever, i dont wanna use another dict💀"""
        attrName = StatHashes.hashToEnum(_statHash).name.lower() + "Stat"
        if attrName in self.__dir__():
            return self.__getattribute__(attrName)
        else:
            raise ValueError("Invalid stat hash")

    def makeAsciiStatBar(self, _statData: Stat):
        """makes a stat bar for ascii"""
        statValue = round(_statData.baseValue/5)
        bonusValue = round(_statData.sumOfMods()/5)
        statBar = "[" + ("="*statValue) + ("+"*bonusValue) + \
            (" "*(20-statValue - bonusValue))
        statBar += "]: " + str(_statData.baseValue + _statData.sumOfMods())
        return statBar

    def __repr__(self) -> str:
        statLayout = self.weaponData.statLayout
        statStr = ""
        for entry in statLayout:
            statHash = StatHashes.hashToEnum(entry["statHash"])
            statObject = self.getStatAttrFromHash(statHash)  # type: ignore
            statStr += f"{statHash.name}: "
            if entry["displayAsNumeric"] and statObject:
                statStr += f"{statObject.baseValue + statObject.sumOfMods()}\n"
            elif statObject:
                statStr += "\t" + self.makeAsciiStatBar(statObject) + "\n"
        return f"{self.name}: {self.weaponType.name}\n"+statStr

    def configFiring(self, _firingSettings: FiringConfig) -> None:
        self.firingSettings = _firingSettings

    # def delPerk(self, _perk: Type[Perk]) -> None:
    #     for perk in self.__perks:
    #         if isinstance(perk, _perk):
    #             perk.remove(self)
    #             self.__perks.remove(perk)
    #             return

    # def addPerk(self, _perk: Type[Perk]) -> None:
    #     self.delPerk(_perk)
    #     try:
    #         prk = _perk() #type: ignore
    #     except:
    #         return
    #     self.__perks.append(prk)
    #     prk.apply(self)

    # def onValueChanged(self) -> None:
    #     """called when a value is changed"""
    #     for perk in self.__perks:
    #         perk.update(self)

    # def addUiElement(self, _element: Union[PerkSlider, PerkToggle]) -> None:
    #     if isinstance(_element, PerkSlider):
    #         self.UI_Sliders.append(_element)
    #     elif isinstance(_element, PerkToggle):
    #         self.UI_Toggles.append(_element)

    # def removeUiElement(self, _element: Union[PerkSlider, PerkToggle]) -> None:
    #     if isinstance(_element, PerkSlider):
    #         self.UI_Sliders.remove(_element)
    #     elif isinstance(_element, PerkToggle):
    #         self.UI_Toggles.remove(_element)

    def getReserves(self) -> int:
        # TODO: try and figure out formula for reserves
        if self.ammoType == AmmoType.PRIMARY:
            return 9999
        return 20

    def getReloadTime(self) -> float:
        if self.weaponFrame.reloadData:
            return calcReload(self.weaponFrame.reloadData, self.reloadStat.val(), self.reloadStat.associatedScalar)
        return 0.0

    def getDps(self, _damage: float, _shotsMissed: int = 0, _isChargeTime: bool = False) -> list[float]:
        """calculates the dps of the weapon"""
        if self.weaponType == WeaponType.SWORD:
            return []
        if self.weaponType == WeaponType.GRENADELAUNCHER:
            return []
        return calcDPS(self.firingSettings.burstDelay, _damage, self.critMult, self.getReloadTime(), self.magazineStat.val(), self.getReserves(),
                    _isChargeTime, _shotsMissed, self.refunds)

    def graphDPS(self, _damage: float):
        pass

    def getTtk(self, _resilience: int, _damage: float, _critMult: float) -> dict[str, Union[int, float]]:
        return calcTtk(self.firingSettings.burstDelay, _resilience, _damage, _critMult, self.magazineStat.val())
