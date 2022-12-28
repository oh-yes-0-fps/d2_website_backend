

from typing import Optional


def calcReload(_infoDict: dict[str, float], _reloadStat: int, _durationScaler: float) -> float:
    """calculates reload stats"""
    a = _infoDict["a"]
    b = _infoDict["b"]
    c = _infoDict["c"]

    return (a*(_reloadStat**2) + b*_reloadStat + c) * _durationScaler


def calcRange(_infoDict: Optional[dict[str, float]], _rangeStat: int, _zoomStat: int, _hipfireMult: float) -> dict[str, float]:
    """calculates range stats"""
    if not _infoDict:
        return {
            "hipFalloffStart": 0.0,
            "hipFalloffEnd": 0.0,
            "falloffStart": 0.0,
            "falloffEnd": 0.0
        }
    zoom = _infoDict["zrm"]
    zoomTier = _infoDict["zrm_tier"]
    vpp = _infoDict["vpp"]
    baseMin = _infoDict["base_min"]
    baseMax = _infoDict["base_max"]

    newZoom = (_zoomStat - zoomTier) / 10 + zoom

    hipFallOffStart = (_rangeStat * vpp + baseMin) * _hipfireMult
    hipFallOffEnd = (_rangeStat * vpp + baseMax) * _hipfireMult

    falloffStart = (_rangeStat * vpp + baseMin) * newZoom
    falloffEnd = (_rangeStat * vpp + baseMax) * newZoom

    outDict = {
        "hipFalloffStart": hipFallOffStart,
        "hipFalloffEnd": hipFallOffEnd,
        "falloffStart": falloffStart,
        "falloffEnd": falloffEnd
    }

    return outDict


def damageAtRange(_inDict: dict[str, float], _maxDmg: float, _minDmg: float, _atRangeInMeters: float, _hipFire: bool) -> float:
    """calculates damage at range"""

    def lerp(_a: float, _b: float, _t: float) -> float:
        return _a + _t * (_b - _a)

    hipFallOffStart = _inDict["hipFallOffStart"]
    hipFallOffEnd = _inDict["hipFallOffEnd"]
    falloffStart = _inDict["falloffStart"]
    falloffEnd = _inDict["falloffEnd"]

    if _hipFire:
        t = (_atRangeInMeters - hipFallOffStart) / \
            (hipFallOffEnd - hipFallOffStart)
    else:
        t = (_atRangeInMeters - falloffStart) / (falloffEnd - falloffStart)

    t = max(0, min(1, t))

    return lerp(_minDmg, _maxDmg, t)


def calcHandling(_infoDict: dict[str, float], _handlingStat: int, _handlingMult: float) -> dict[str, float]:
    """calculates handling stats"""
    readyVpp = _infoDict["readyVpp"]
    readyBase = _infoDict["readyBase"]

    stowVpp = _infoDict["stowVpp"]
    stowBase = _infoDict["stowBase"]

    # the results maybe in frames at 60fps?, so to turn to seconds we divide by 60| TODO: confirm this
    readyTime = ((readyVpp * _handlingStat + readyBase) * _handlingMult) / 60
    stowTime = ((stowVpp * _handlingStat + stowBase) * _handlingMult) / 60

    outDict = {
        "readyTime": readyTime,
        "stowTime": stowTime
    }

    return outDict
