from util.DamageCalc import *

def swordCalc(_impact: int, _pveMult:float) -> float:
    return ((2.55*_pveMult)*_impact) + 96.5*_pveMult

rpl = 1350

activity = Activity(rpl,DifficultyOptions.NORMAL, "Enclave", 0)

base = 88

damage = calcDmgPve(activity, base, rpl)

damageMult = damage/base

inGame = 8591

# print(f"Damage: {damage}")
print(f"Damage Mult: {damageMult}")
swordDmg = swordCalc(60, damageMult)
print(swordDmg)
print(swordDmg/inGame)
# print(f"{inGame/damageMult}/{base} = {round((inGame/damageMult)/base,3)}")

