from typing import Union
from util.DamageCalc import *
import json

def swordCalc(_impact: int, _pveMult:float) -> float:
    return ((2.55*_pveMult)*_impact) + 96.5*_pveMult



rpl = 1578

activity = Activity(rpl,DifficultyOptions.NORMAL, "Enclave", 0)

base = 139

damage = calcDmgPve(activity, base, rpl, _enemyType = EnemyType.MINIBOSS, _buffs = BuffPackage(PVE=[1.101], MINIBOSS=[1.81]))

damageMult = damage/base

inGame = 12619

print(f"Damage: {damage}")
# print(f"Damage Mult: {damageMult}")
# swordDmg = swordCalc(60, damageMult)
# print(swordDmg)
# print(swordDmg/inGame)
print(f"{inGame/damageMult}/{base} = {round((inGame/damageMult)/base,3)}")

