

from dataclasses import dataclass, field
from math import ceil
from typing import Any, Optional, Tuple, Type, Union
# from perks.Perks import Perk, PerkSlider, PerkToggle  # Weapons.
from Enums import AmmoType, DamageType, EnemyType, WeaponSlot, WeaponType, StatHashes
from util.AmmoCalc import lerp
from util.DpsCalc import calcDPS, calcRefund
from util.TtkCalc import calcTtk
from util.StatCalc import calcReload, calcHandling, calcRange
from util.DamageCalc import calcDmgPve, BuffPackage, Activity, calcDmgPvp
from ApiInterface import APIWeaponData, FiringConfig, FrameData


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

        self.magSizeBounds = []
        for i in self.weaponData.statLayout:
            if i["statHash"] == StatHashes.MAGAZINE.value:
                self.magSizeBounds = i["displayInterpolation"]


        self.name = _weaponData.name

        self.impactStat = Stat(l_weaponStats.get(StatHashes.IMPACT, -1))
        self.rangeStat = Stat(l_weaponStats.get(StatHashes.RANGE, -1))
        self.stabilityStat = Stat(l_weaponStats.get(StatHashes.STABILITY, -1))
        self.handlingStat = Stat(l_weaponStats.get(StatHashes.HANDLING, -1))
        self.reloadStat = Stat(l_weaponStats.get(StatHashes.RELOAD, -1))
        self.aim_assistStat = Stat(
            l_weaponStats.get(StatHashes.AIM_ASSIST, -1))
        self.zoomStat = Stat(l_weaponStats.get(StatHashes.ZOOM, -1))
        self.airborneStat = Stat(l_weaponStats.get(StatHashes.AIRBORNE, -1))
        self.recoil_dirStat = Stat(
            l_weaponStats.get(StatHashes.RECOIL_DIR, -1))
        self.rpmStat = Stat(l_weaponStats.get(StatHashes.RPM, -1))
        self.magazineStat = Stat(l_weaponStats.get(StatHashes.MAGAZINE, -1))
        self.inventory_sizeStat = Stat(
            l_weaponStats.get(StatHashes.INVENTORY_SIZE, -1))
        self.velocityStat = Stat(l_weaponStats.get(StatHashes.VELOCITY, -1))
        self.blast_radiusStat = Stat(
            l_weaponStats.get(StatHashes.BLAST_RADIUS, -1))
        self.draw_timeStat = Stat(l_weaponStats.get(StatHashes.DRAW_TIME, -1))
        self.swing_speedStat = Stat(
            l_weaponStats.get(StatHashes.SWING_SPEED, -1))
        self.charge_timeStat = Stat(
            l_weaponStats.get(StatHashes.CHARGE_TIME, -1))
        self.guard_efficiencyStat = Stat(
            l_weaponStats.get(StatHashes.GUARD_EFFICIENCY, -1))
        self.guard_enduranceStat = Stat(
            l_weaponStats.get(StatHashes.GUARD_ENDURANCE, -1))
        self.guard_resistanceStat = Stat(
            l_weaponStats.get(StatHashes.GUARD_RESISTANCE, -1))
        self.charge_rateStat = Stat(
            l_weaponStats.get(StatHashes.CHARGE_RATE, -1))
        self.shield_durationStat = Stat(
            l_weaponStats.get(StatHashes.SHIELD_DURATION, -1))

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

    def getStatAttrFromHash(self, _statHash: StatHashes) -> Stat:
        """returns the stat attribute from the hash"""
        """This is the most scuffed thing ever, i dont wanna use another dict💀"""
        attrName = _statHash.name.lower() + "Stat"
        if attrName in self.__dir__():
            return self.__getattribute__(attrName)
        else:
            raise ValueError(f"Invalid stat hash: {_statHash}")

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
            statStr += "\n"
            statHash = StatHashes.hashToEnum(entry["statHash"])
            if statHash != StatHashes.MAGAZINE:
                statObject = self.getStatAttrFromHash(statHash)  # type: ignore
            else:
                statObject = Stat(self.magSize)
            statStr += f"{statHash.name + ': ':16}"
            if entry["displayAsNumeric"] and statObject:
                statStr += f"{statObject.baseValue + statObject.sumOfMods()}"
            elif statObject:
                statStr += self.makeAsciiStatBar(statObject)
        return f"{self.name}: {self.weaponType.name}\n"+statStr+"\n"

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
    @property
    def totalReserves(self) -> int:
        # TODO: try and figure out formula for reserves
        if self.ammoType == AmmoType.PRIMARY:
            return self.magSize*5
        return 20

    @property
    def magSize(self) -> int:
        keyId = 0
        for i in range(len(self.magSizeBounds)):
            if self.magazineStat.val() <= self.magSizeBounds[i]["value"]:
                keyId = i-1
                break
        if keyId:
            if self.magazineStat.val() == self.magSizeBounds[keyId]["value"]:
                return self.magSizeBounds[keyId]["weight"]
            t = (self.magazineStat.val() - self.magSizeBounds[keyId]["value"]/
                    self.magSizeBounds[keyId+1]["value"]-self.magSizeBounds[keyId]["value"])
            return ceil(lerp(self.magSizeBounds[keyId]["weight"], self.magSizeBounds[keyId+1]["weight"], t))
        return 1

    @property
    def reloadTime(self) -> float:
        if self.weaponFrame.reloadData and self.reloadStat:
            return calcReload(self.weaponFrame.reloadData, self.reloadStat.val(), self.reloadStat.associatedScalar)
        return 0.0

    def getDamage(self, _rpl:int, _gpl:int, _enemyType:EnemyType) -> float:
        #TODO
        inDmg = self.baseDamage * self.firingSettings.burstSize
        return calcDmgPve(Activity(_rpl), inDmg, _gpl, _enemyType = _enemyType, _buffs = self.damageScalars)

    def getDps(self, _damage: float, _shotsMissed: int = 0) -> list[float]:
        """calculates the dps of the weapon"""
        if self.weaponType == WeaponType.SWORD:
            return []
        if self.weaponType == WeaponType.GRENADELAUNCHER:
            return []
        return calcDPS(self.firingSettings, _damage, self.critMult, self.reloadTime, self.magSize, self.totalReserves,
                        _shotsMissed, self.refunds)

    def graphDPS(self, _damage: float):
        pass

    def getTtk(self, _resilience: int) -> dict[str, Union[int, float]]:
        damage = calcDmgPvp(self.baseDamage, self.damageScalars)
        if self.weaponType == WeaponType.SHOTGUN and self.critMult < 1.15:
            critMult = 1.0
        else:
            critMult = self.critMult
        return calcTtk(self.firingSettings, _resilience, damage, critMult, self.magazineStat.val())

    def getRange(self) -> dict[str, float]:
        return calcRange(self.weaponFrame.rangeData, self.rangeStat.val(), self.zoomStat.val(), self.hipFireRangeScalar)