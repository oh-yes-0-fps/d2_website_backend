



from math import ceil

def rpmToDelay(_rpm: int) -> float:
    """converts rpm to shot delay"""
    return 60/_rpm

def timeToEmpty(_mag:int,_delay:float,_burstDuration:float) -> float:
    return (_mag*_burstDuration) + ((_mag-1)*_delay)

rof = 200
dmg = 1_000
critMult = 1.5
reload = 1.8
magSize = 8
reserves = 27
isChargeTime = False

fireDelay = rpmToDelay(rof)

numOfMags = ceil(reserves/magSize)
sizeOfLastMag = round((reserves/magSize-(numOfMags-1))*magSize)

if isChargeTime:
    reload += fireDelay
    #This just accounts for having to charge up again after a reload
timeTaken = 0.0
damageDealt = 0.0
dpsPerMag = []
for i in range(numOfMags):
    magIDX = i + 1
    if magIDX == numOfMags:
        _magSize = sizeOfLastMag
    else:
        _magSize = magSize

    if magIDX > 1:
        timeTaken += reload

    timeTaken += timeToEmpty(_magSize,fireDelay,0)
    damageDealt += _magSize*dmg

    dpsPerMag.append(damageDealt/timeTaken)


