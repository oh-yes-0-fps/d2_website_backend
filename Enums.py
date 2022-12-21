from enum import Enum

#Contains all enums use in main directory
#stuff in util has its own self containe enums

class PartType(Enum):
    GUN = 1
    EXPLOSIVE = 2
    SWORD = 3
    GLAIVE = 4
    BATTERY = 5

class AmmoTypes(Enum):
    PRIMARY = 1
    SPECIAL = 2
    HEAVY = 3

class WeaponType(Enum):
    """used to determine the type of weapon"""
    HANDCANNON = 1
    AUTORIFLE = 2
    SHOTGUN = 3
    SNIPER = 4
    ROCKET = 5
    GLAIVE = 6
    TRACERIFLE = 7
    SIDEARM = 8
    SWORD = 9
    BOW = 10
    FUSIONRIFLE = 11
    MACHINEGUN = 12
    LINEARFUSIONRIFLE = 13
    GRENADELAUNCHER = 14
    SUBMACHINEGUN = 15
    PULSERIFLE = 16
    SCOUTRIFLE = 17


class IntrinsicFrame(Enum):
    # "Standard" ones
    AGGRESSIVE = 1
    ADAPTIVE = 2
    PRECISION = 3
    HIGH_IMPACT = 4
    LIGHT_WEIGHT = 5
    RAPID_FIRE = 6

    # niche ones, would like to condense these
    # GL
    WAVE = 7
    # SG
    PINPOINT_SLUG = 8
    # SWORD
    CASTER = 9
    VORTEX = 10
    # SIDEARM
    AGGRESSIVE_BURST = 11
    ADDAPTIVE_BURST = 12

class StatBuffID(Enum):
    GUN_DAMAGE = "Weapon Damage"
    RANGE = "Weapon Range"
    STABILITY = "Weapon Stability"
    RELOAD = "Weapon Reload Speed"
    MAGAZINE = "Weapon Magazine Size"
    HANDLING = "Weapon Handling Speed"
    VELOCITY = "Weapon Velocity"
    BLAST_RADIUS = "Weapon Blast Radius"
    AIM_ASSIST = "Weapon Target Acquisition"
    AIRBORNE_EFFECTIVENESS = "Weapon Airborne Effectiveness"
    RECOIL_DIRECTION = "Weapon Recoil Direction"
    RPM = "Weapon Rate of Fire"
    CHARGE_TIME = "Weapon Charge Time"
    INVENTORY_SIZE = "Weapon Reserves"
    ZOOM = "Weapon Zoom"
    #not visible anywhere but like exist? god i wish wasnt custom engine
    ACCURACY = "Weapon Accuracy"
    RECOIL = "Weapon Kick"
    #TODO:SWORDS

    #Player
    RESILIENCE = "Player Resilience"
    RECOVERY = "Player Recovery"
    MOBILITY = "Player Mobility"
    DISCIPLINE = "Player Discipline"
    INTELLECT = "Player Intellect"
    STRENGTH = "Player Strength"
    DAMAGE_REDUCTION = "Damage Resistance"
    MOVEMENT_SPEED = "Player Move Speed"
    MELEE_DMG = "Melee Damage"
    GRENADE_DMG = "Grenade Damage"
    SUPER_DMG = "Super Damage"
    MELEE_CD = "Melee CoolDown"
    GRENADE_CD = "Grenade CoolDown"
    SUPER_CD = "Super CoolDown"
    CLASS_ABIL_CD = "Class Ability CoolDown"

class EnemyType(Enum):
    MINOR = "MINOR"
    ELITE = "ELITE"
    MINIBOSS = "MINIBOSS"
    BOSS = "BOSS"
    VEHICLE = "VEHICLE"