from dataclasses import dataclass, field
import json
from Enums import WeaponType

jdata = {}

@dataclass()
class WepData:
    rpm:int = field(default_factory=lambda: 0)
    burstSize:int = field(default_factory=lambda: 1)
    burstDuration:float = field(default_factory=lambda: 0.0)
    chargeTime:float = field(default_factory=lambda: 0.0)
    damage:dict[str, float] = field(default_factory=lambda: {"PVE":0.0, "PVP":0.0})
    critMult:float = field(default_factory=lambda: 1.0)
    range:dict[str, float] = field(default_factory=lambda: {"MIN":0.0, "MAX":0.0})
    handling:dict[str, float] = field(default_factory=lambda: {"MIN":0.0, "MAX":0.0})

    def fromDict(self, _dict:dict) -> None:
        self.rpm = _dict["rpm"]
        self.burstSize = _dict["burstSize"]
        self.burstDuration = _dict["burstDuration"]
        self.chargeTime = _dict["chargeTime"]
        self.damage = _dict["damage"]
        self.critMult = _dict["critMult"]
        self.range = _dict["range"]
        self.handling = _dict["handling"]


for i in WeaponType._member_names_:
    jdata[str(i)] = WepData().__dict__
