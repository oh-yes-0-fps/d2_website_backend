from dataclasses import dataclass, field
from typing import Optional, Tuple
# from DataCurve import DataCurve, CurveKey
from util.DataCurve import DataCurve, CurveKey
from Enums import EnemyType
from enum import Enum


NORMAL_DELTA_DATA = [(0,1),(-10,0.78),(-20,0.66),(-30,0.5914),(-40,0.5405),(-50,0.5),(-60,0.475),
                    (-70,0.46),(-80,0.44),(-90,0.42),(-99,0.418)]
RAID_DELTA_DATA = [(0,0.925),(-10,0.73),(-20,0.62),(-30,0.5632),(-40,0.5252),(-50,0.495),(-60,0.475)]
MASTER_DELTA_DATA = [(0,0.85),(-10,0.68),(-20,0.58),(-30,0.5336),(-40,0.505),(-50,0.485),(-60,0.475)]
WEAPON_DELTA_EXPONENT = 1.006736


class DifficultyData:
    def __init__(self, _name: str, _curve: list[Tuple[int, float]], _cap: int):
        self.name = _name
        self.cap = _cap
        keyLst = []
        for i in _curve:
            keyLst.append(CurveKey(i[0], i[1]))
        self.gearCurve = DataCurve(*keyLst)
        self.gearCurve.finalize()

class DifficultyOptions(Enum):
    NORMAL = DifficultyData("Normal", NORMAL_DELTA_DATA, 50)
    RAID_DUNGEON = DifficultyData("Raid & Dungeon", RAID_DELTA_DATA, 20)
    MASTER = DifficultyData("Master", MASTER_DELTA_DATA, 20)

class Activity:
    def __init__(self, _reccomendedPL:int, _difficulty: DifficultyOptions = DifficultyOptions.NORMAL, _name: str = "Custom", _overrideCap: Optional[int] = None):
        self.name = _name
        self.difficulty = _difficulty
        self.rPL = _reccomendedPL
        if _overrideCap is None:
            self.overrideCap:int = _difficulty.value.cap
        else:
            self.overrideCap:int = _overrideCap

@dataclass()
class BuffPackage:
    PVP: list = field(default_factory=list)
    PVE: list = field(default_factory=list)
    MINOR: list = field(default_factory=list)
    ELITE: list = field(default_factory=list)
    MINIBOSS: list = field(default_factory=list)
    BOSS: list = field(default_factory=list)
    VEHICLE: list = field(default_factory=list)

    def getBuffValuePVE(self, _type: str) -> float:
        v1 = listProduct(self.PVE)
        v2 = 1.0
        if _type == "MINOR":
            v2 = listProduct(self.MINOR)
        elif _type == "ELITE":
            v2 = listProduct(self.ELITE)
        elif _type == "MINIBOSS":
            v2 = listProduct(self.MINIBOSS)
        elif _type == "BOSS":
            v2 = listProduct(self.BOSS)
        elif _type == "VEHICLE":
            v2 = listProduct(self.VEHICLE)
        return v1 * v2

    def getBuffValuePVP(self) -> float:
        return listProduct(self.PVP)

    def addPVE_PVP(self, _value: float):
        self.PVP.append(_value)
        self.PVE.append(_value)


def listProduct(list1) -> float:
    product = 1
    for i in list1:
        product *= i
    return product


def rplToMult(rpl: int) -> float:
    return (1 + ((1/30) * rpl))/(1 + 1/3)


def plDelta(_rpl: int, _gpl:int, _difficulty:DifficultyOptions, _overrideCap:int = 100 ) -> float:
    """Assumes weapon and gear PL are the same"""
    difficultyData:DifficultyData = _difficulty.value
    curve = difficultyData.gearCurve
    delta = _gpl - _rpl
    if delta <= -100:
        return 0 #enemies are immune below -99
    if delta >= _overrideCap:
        delta = _overrideCap
    if delta < -60:
        curve = DifficultyOptions.NORMAL.value.gearCurve
    wepDeltaMult = WEAPON_DELTA_EXPONENT**delta
    gearDeltaMult = curve.eval(delta)
    return wepDeltaMult * gearDeltaMult



def calcDmgPve(_activity: Activity, _baseDmg: float, _gpl: int, _worldBonuses:float = 1.0, _enemyType:EnemyType = EnemyType.BOSS,
                _buffs: BuffPackage = BuffPackage()) -> float:
    """Does not account for crit damage and crit buffs, world bonuses are like kinetic buff, burns, heavyweaight etc"""
    buff_mod = _buffs.getBuffValuePVE(_enemyType.value)

    rPL = _activity.rPL
    rPL_Mult = rplToMult(rPL)

    #I'm going to assume weapon and gear PL are the same, separating makes more complicated for user
    difficulty = _activity.difficulty
    deltaMult = plDelta(rPL, _gpl, difficulty, _activity.overrideCap)

    return _baseDmg * (rPL_Mult * buff_mod * deltaMult * _worldBonuses)

def calcDmgPvp(_baseDmg :float, _buffs: BuffPackage = BuffPackage()) -> float:
    """Does not account for crit damage or crit buffs"""
    buff_mod = _buffs.getBuffValuePVP()
    return _baseDmg * buff_mod