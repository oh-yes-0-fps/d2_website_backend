


def lerp(_start:float, _end:float, _t:float) -> float:
    return _start + _t*(_end - _start)

def getDecimal(n):
    return n - int(n)

def roundUp(n):
    return int(n) + 1

def calcReserve(_invSizeStat:int, _m:float, _b:float) -> int:
    return roundUp(_m*_invSizeStat + _b)

def calcMag(_magSizeStat:int, _m:float, _b:float) -> int:
    return roundUp(_m*_magSizeStat + _b)

