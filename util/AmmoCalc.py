




def getDecimal(n):
    return n - int(n)


def calcReserve(_invSizeStat:int, _m:float, _b:float) -> int:
    return round(_m*_invSizeStat + _b)

def calcMag(_magSizeStat:int, _m:float, _b:float) -> int:
    return round(_m*_magSizeStat + _b)

