



from math import ceil
from typing import Any



def __timeToEmpty(_mag:int,_delay:float,_burstDuration:float) -> float:
    return (_mag*_burstDuration) + ((_mag-1)*_delay)

def calcRefund(_magSize:int, _critsMissed:int, _refunds:list[dict[str,Any]]) -> int:
    """This is by far the slowest thing here with requiring a while loop,
    I could just have static formula for existing perks but thats cringe"""
    if len(_refunds) == 0:
        return _magSize
    currMag = _magSize
    shotsFired = 0
    while currMag:
        isCrit = True
        if shotsFired < _critsMissed:
            isCrit = False
        shotsFired += 1
        for refund in _refunds: #💀python loops
            if refund["CRIT"] == isCrit or refund["CRIT"] == False:
                req = refund["REQUIREMENT"]
                if shotsFired/req == int(shotsFired/req):
                    currMag += refund["REFUND"]
        currMag -= 1
    return shotsFired# aka mag size

def calcDPS(_fireDelay:float,_dmg:float,_critMult:float,_reload:float,_magSize:int,_reserves:int,
            _isChargeTime:bool, _critsMissed:int = 0, _refunds:list[dict] = []) -> list[float]:
    numOfMags = ceil(_reserves/_magSize)
    sizeOfLastMag = round((_reserves/_magSize-(numOfMags-1))*_magSize)

    if _isChargeTime:
        _reload += _fireDelay
        #This just accounts for having to charge up again after a reload
    timeTaken = 0.0
    damageDealt = 0.0
    dpsPerMag = []
    for i in range(numOfMags):
        magIDX = i + 1
        if magIDX == numOfMags:
            f_magSize = calcRefund(sizeOfLastMag,_critsMissed,_refunds)
        else:
            f_magSize = calcRefund(_magSize,_critsMissed,_refunds)

        if magIDX > 1:
            timeTaken += _reload

        timeTaken += __timeToEmpty(f_magSize,_fireDelay,0)
        damageDealt += f_magSize*(_dmg*(_critMult*((f_magSize-_critsMissed)/f_magSize)))

        dpsPerMag.append(damageDealt/timeTaken)
    return dpsPerMag


