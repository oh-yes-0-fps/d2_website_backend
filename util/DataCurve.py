from enum import Enum
from typing import Union


ONETHIRD: float = 1/3

tang_tension = 0
TANG_MULTIPLIER = 2


class InterpMode(Enum):
    LINEAR = 0
    MANUAL = 1
    CUBIC = 2
    CONSTANT = 3
    LAGRANGE = 4

    @staticmethod
    def fromStr(string: str):
        if string in InterpMode.__members__:
            return InterpMode[string]
        else:
            raise ValueError(f"Invalid interpMode: {string}")


class Tangent:
    def __init__(self, _arrive: float = 0, _leave: float = 0):
        self.arrive = _arrive
        self.leave = _leave

    def fromTuple(self, _inTuple: tuple):
        if len(_inTuple) != 2:
            self.arrive = 0
            self.leave = 0
        else:
            self.arrive = _inTuple[0]
            self.leave = _inTuple[1]
        return self

    def fromFloat(self, _inFloat: float):
        self.arrive = _inFloat
        self.leave = _inFloat
        return self

    def __repr__(self) -> str:
        return f"(a:{self.arrive}, l:{self.leave})"


class CurveKey:
    # just for sorting
    @staticmethod
    def getValue(key) -> float:
        return key.value

    @staticmethod
    def getTime(key) -> float:
        return key.time

    def __init__(self, _time: float, _value: float, _mode: InterpMode = InterpMode.LINEAR, _tangents: Union[Tangent, tuple] = (0, 0)) -> None:
        self.time = _time
        self.value = _value
        self.mode = _mode
        if isinstance(_tangents, tuple):
            self.tangent: Tangent = Tangent().fromTuple(_tangents)
        else:
            self.tangent = _tangents

    def setMode(self, _mode: Union[str, InterpMode, int]):
        if isinstance(_mode, str):
            self.mode = InterpMode.fromStr(_mode)
        elif isinstance(_mode, int):
            self.mode = InterpMode(_mode)
        else:
            self.mode = _mode

    def __repr__(self) -> str:
        return f"({self.time}, {self.value}, {self.mode.name}, {self.tangent})"


class CurveMath:
    @staticmethod
    def AutoCalcTangent(PrevTime: float, PrevPoint: float, CurTime: float, CurPoint: float, NextTime: float, NextPoint: float, Tension: float) -> float:
        outTan: float = (1 - Tension) * \
            (NextPoint-PrevPoint)
        PrevToNextTimeDiff = max(0.1, NextTime - PrevTime)
        print(f'{outTan} / {PrevToNextTimeDiff} = {outTan/PrevToNextTimeDiff}')
        return (outTan/PrevToNextTimeDiff) * TANG_MULTIPLIER

    @staticmethod
    def __Lerp(A: float, B: float, T: float) -> float:
        return A + (B-A)*T

    @staticmethod
    def lagrangeInterp(_keyList: list, _time: float) -> float:
        outValue: float = 0
        for i in range(len(_keyList)):
            curKey: CurveKey = _keyList[i]
            curValue: float = curKey.value
            curTime: float = curKey.time
            curWeight: float = 1
            for j in range(len(_keyList)):
                if i != j:
                    otherKey: CurveKey = _keyList[j]
                    otherTime: float = otherKey.time
                    curWeight *= (_time - otherTime) / (curTime - otherTime)
            outValue += curValue * curWeight
        return outValue

    @staticmethod
    def linInterp(_Key1: CurveKey, _Key2: CurveKey, timeIn: float) -> float:
        diff = _Key2.time - _Key1.time
        timeOffset = (timeIn - _Key1.time) / diff
        return CurveMath.__Lerp(_Key1.value, _Key2.value, timeOffset)

    @staticmethod
    def cubicInterp(_Key1: CurveKey, _Key2: CurveKey, timeIn: float) -> float:
        diff = _Key2.time - _Key1.time
        timeOffset = (timeIn - _Key1.time) / diff

        point0 = _Key1.value
        point1 = _Key1.value + (_Key1.tangent.leave * diff * ONETHIRD)
        point2 = _Key2.value - (_Key2.tangent.arrive * diff * ONETHIRD)
        point3 = _Key2.value

        p01 = CurveMath.__Lerp(point0, point1, timeOffset)
        p12 = CurveMath.__Lerp(point1, point2, timeOffset)
        p23 = CurveMath.__Lerp(point2, point3, timeOffset)
        p012 = CurveMath.__Lerp(p01, p12, timeOffset)
        p123 = CurveMath.__Lerp(p12, p23, timeOffset)
        p0123 = CurveMath.__Lerp(p012, p123, timeOffset)
        return p0123


class DataCurve:
    def __init__(self, *args: CurveKey):
        self.keys: list[CurveKey] = []
        for i in args:
            if isinstance(i, CurveKey):
                self.keys.append(i)
        self.keys.sort(key=CurveKey.getTime)

    def addKeys(self, *args: CurveKey):
        for i in args:
            if isinstance(i, CurveKey):
                self.keys.append(i)
        return sorted(self.keys, key=CurveKey.getTime)

    def addKeysList(self, _inList: list[CurveKey]):
        return self.addKeys(*_inList)

    def finalize(self, tension=0):
        for i in range(len(self.keys)):
            _Ky = self.keys[i]
            if _Ky.mode == InterpMode.CUBIC:
                if i == len(self.keys)-1 or i == 0:
                    # _Ky.tangent.leave = 0
                    # _Ky.tangent.arrive = 0
                    continue
                p_Ky = self.keys[i-1]
                n_Ky = self.keys[i+1]
                tang = CurveMath.AutoCalcTangent(
                    p_Ky.time, p_Ky.value, _Ky.time, _Ky.value, n_Ky.time, n_Ky.value, tension)
                _Ky.tangent.leave = tang
                _Ky.tangent.arrive = tang

    def eval(self, timeIn: float) -> float:
        for i in range(len(self.keys)):
            _Ky = self.keys[i]
            if _Ky.time > timeIn:
                if i == 0:
                    return _Ky.value
                p_Ky = self.keys[i-1]
                if _Ky.mode == InterpMode.LINEAR:
                    return CurveMath.linInterp(p_Ky, _Ky, timeIn)
                elif _Ky.mode == InterpMode.CUBIC or _Ky.mode == InterpMode.MANUAL:
                    return CurveMath.cubicInterp(p_Ky, _Ky, timeIn)
                elif _Ky.mode == InterpMode.LAGRANGE:
                    return CurveMath.lagrangeInterp(self.keys, timeIn)
                else:
                    return p_Ky.value
        return self.keys[-1].value

    def getTimeRange(self) -> tuple[float, float]:
        return self.keys[0].time, self.keys[-1].time
