from __future__ import annotations
from ..Weapons import Weapon


# PERKS:
#   CATEGORIES: implementation
#       On kill
#           dict of statbuff dataclass
#       On hit(Rapid hit, )
#           list of statbuff dataclass
#       On kill reload(Tunnel vision, kill clip, etc.)
#           list of statbuff dataclass
#       On timer/duration condition(Tunnel vision, frenzy, One Quiet Moment, etc.)
#           list of statbuff dataclass
#       On constant
#       Basic toggle condition
#
#       NonImplementable
#           Just a description
from typing import Any, Tuple, Union
from typing_extensions import override
from Enums import StatBuffID


class StatBuff:
    def __init__(self, _stat: StatBuffID, _value: float, _toScale: bool = False) -> None:
        self.stat = _stat
        self.value = _value
        self.scale = _toScale

    def __repr__(self) -> str:
        if self.scale:
            ez_read_val = ""
            if self.value < 0:
                ez_read_val = "-" + str(abs(self.value-1)) + "%"
            else:
                ez_read_val = "+" + str(self.value-1) + "%"
        else:
            ez_read_val = str(self.value)
        return f"{self.stat.value}: {ez_read_val}"

class PerkSlider:
    def __init__(self, _name: str, _desc: str, _min: int, _max: int, _default: int) -> None:
        self.name = _name
        self.desc = _desc
        self.min = _min
        self.max = _max
        self.default = _default
        self.value = _default

    def __repr__(self) -> str:
        return f"{self.name}: {self.min}->{self.max} at {self.value}"

    def set(self, _value: int) -> None:
        if _value < self.min:
            self.value = self.min
        elif _value > self.max:
            self.value = self.max
        else:
            self.value = _value

    def get(self) -> int:
        return self.value

class PerkToggle:
    def __init__(self, _name: str, _desc: str, _default: bool) -> None:
        self.name = _name
        self.desc = _desc
        self.default = _default
        self.value = _default

    def __repr__(self) -> str:
        return f"{self.name}: {self.value}"

    def toggle(self) -> None:
        self.value = not self.value

    def get(self) -> bool:
        return self.value


class Perk:
    ratings = {"PVP": "Unranked", "PVE": "Unranked"}
    def __init__(self, _name: str, _desc: str, _statBuffs: list[StatBuff]) -> None:
        self.name = _name
        self.desc = _desc
        self.__statBuffs = _statBuffs
        self.__weaponLimitations = []
        self.shouldUpdate = False

    def __repr__(self) -> str:
        return self.name

    def apply(self, _weapon: Weapon, **kwArgs) -> None:
        pass

    def remove(self, _weapon: Weapon, **kwArgs) -> None:
        pass

    def update(self, _weapon: Weapon, **kwArgs) -> None:
        pass

    def getDesc(self) -> str:
        return f"Not implemented yet on {__name__}"


class IntCondPerk(Perk):
    """A perk that would need a slider to set the value of the statbuffs"""
    def __init__(self, _name: str, _desc: str, _statBuffs: dict[int, list[StatBuff]], _slider: PerkSlider) -> None:
        super().__init__(_name, _desc, _statBuffs.get(0, []))
        self._newStatBuffs = _statBuffs
        self._slider = _slider

    def apply(self, _weapon: Weapon, **kwArgs) -> None:
        super().apply(_weapon, **kwArgs)
        _weapon.addUiElement(self._slider)

    def remove(self, _weapon: Weapon, **kwArgs) -> None:
        super().remove(_weapon, **kwArgs)
        _weapon.removeUiElement(self._slider)

class BoolCondPerk(Perk):
    """A perk that would need a toggle to set the value of the statbuffs"""
    def __init__(self, _name: str, _desc: str, _statBuffs: dict[bool, list[StatBuff]], _toggle: PerkToggle) -> None:
        super().__init__(_name, _desc, _statBuffs.get(False, []))
        self._newStatBuffs = _statBuffs
        self._toggle = _toggle

    def apply(self, _weapon: Weapon, **kwArgs) -> None:
        super().apply(_weapon, **kwArgs)
        _weapon.addUiElement(self._toggle)

    def remove(self, _weapon: Weapon, **kwArgs) -> None:
        super().remove(_weapon, **kwArgs)
        _weapon.removeUiElement(self._toggle)

class RefundPerk(Perk):
    def __init__(self, _name: str, _desc: str, _statBuffs: list[StatBuff], _refundData: dict[str, Union[str, bool]]) -> None:
        super().__init__(_name, _desc, _statBuffs)
        self.refundData = _refundData

    def apply(self, _weapon: Weapon) -> None:
        super().apply(_weapon)
        _weapon.refunds.append(self.refundData)

    def remove(self, _weapon: Weapon, **kwArgs) -> None:
        super().remove(_weapon, **kwArgs)
        _weapon.refunds.remove(self.refundData)

class StaticPerk(Perk):
    """Weapon parts and intrinsic frames will almost always fall under this"""
    def __init__(self, _name: str, _desc: str, _statBuffs: list[StatBuff]) -> None:
        super().__init__(_name, _desc, _statBuffs)

    def apply(self, _weapon: Weapon) -> None:
        super().apply(_weapon)
        _weapon.addStatBuffs(self.__statBuffs)#TODO

    def remove(self, _weapon: Weapon) -> None:
        super().remove(_weapon)
        _weapon.removeStatBuffs(self.__statBuffs)
