

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
                ez_read_val = "-" + abs(str(self.value-1)) + "%"
            else:
                ez_read_val = "+" + str(self.value-1) + "%"
        else:
            ez_read_val = str(self.value)
        return f"{self.stat.value}: {ez_read_val}"


class Perk:
    def __init__(self, _name: str, _desc: str, _statBuffs: list[StatBuff]) -> None:
        self.name = _name
        self.desc = _desc
        self.__statBuffs = _statBuffs
        self.__weaponLimitations = []

    def __repr__(self) -> str:
        return self.name

    def addRefund(self, _weapon: Any) -> None:
        pass

    def getDesc(self) -> str:
        # Could have made this a repr but that would get messy
        desc = f"\n# {self.name}\n"
        desc += self.desc
        for i in self.__statBuffs:
            desc += "\n"
            desc += str(i)
        return desc


class OnKill(Perk):
    def __init__(self, _name: str, _desc: str, _statBuffs: dict[int, list[StatBuff]]) -> None:
        super().__init__(_name, _desc, _statBuffs.get(0, []))
        self._newStatBuffs = _statBuffs

    def getDesc(self) -> str:
        pass


class Refund(Perk):
    def __init__(self, _name: str, _desc: str, _statBuffs: list[StatBuff], _refundData: dict[str, Union[str, bool]]) -> None:
        super().__init__(_name, _desc, _statBuffs)
        self.refundData = _refundData

    def addRefund(self, _weapon: Any) -> None:
        _weapon.refunds.append(self.refundData)
