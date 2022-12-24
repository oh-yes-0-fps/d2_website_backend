from enum import Enum

# Contains all enums use in main directory
# stuff in util has its own self containe enums


class AmmoType(Enum):
    PRIMARY = 1
    SPECIAL = 2
    HEAVY = 3
    UNKNOWN = 0

    @staticmethod
    def getEnumFromHash(_hash: int):
        if _hash == 1:
            return AmmoType.PRIMARY
        elif _hash == 2:
            return AmmoType.SPECIAL
        elif _hash == 3:
            return AmmoType.HEAVY
        else:
            return AmmoType.UNKNOWN


class WeaponType(Enum):
    """used to determine the type of weapon"""
    HANDCANNON = 9
    AUTORIFLE = 6
    SHOTGUN = 7
    SNIPER = 12
    ROCKET = 10
    GLAIVE = 33
    TRACERIFLE = 25
    SIDEARM = 17
    SWORD = 18
    BOW = 31
    FUSIONRIFLE = 11
    MACHINEGUN = 8
    LINEARFUSIONRIFLE = 22
    GRENADELAUNCHER = 23
    SUBMACHINEGUN = 24
    PULSERIFLE = 13
    SCOUTRIFLE = 14
    UNKNOWN = 0

    @staticmethod
    def getEnumFromHash(_hash: int) -> 'WeaponType':
        WeaponType._value2member_map_: dict[int, WeaponType]
        return WeaponType._value2member_map_.get(_hash, WeaponType.UNKNOWN)


class EnemyType(Enum):
    MINOR = "MINOR"
    ELITE = "ELITE"
    MINIBOSS = "MINIBOSS"
    BOSS = "BOSS"
    VEHICLE = "VEHICLE"
    ENCLAVE = "ENCLAVE"


class WeaponSlot(Enum):
    KINETIC = 1498876634
    ENERGY = 2465295065
    POWER = 953998645
    UNKNOWN = 0

    @staticmethod
    def getEnumFromHash(hash: int) -> 'WeaponSlot':
        WeaponSlot._value2member_map_: dict[int, WeaponSlot]
        return WeaponSlot._value2member_map_.get(hash, WeaponSlot.UNKNOWN)


class DamageType(Enum):
    ARC = 2303181850
    VOID = 3454344768
    SOLAR = 1847026933
    STASIS = 151347233
    KINETIC = 3373582085
    UNKNOWN = 0

    @staticmethod
    def getEnumFromHash(hash: int) -> 'DamageType':
        DamageType._value2member_map_: dict[int, DamageType]
        return DamageType._value2member_map_.get(hash, DamageType.UNKNOWN)


class StatHashes(Enum):
    ACCURACY = 1591432999
    AIMASSIST = 1345609583
    AIRBORNE = 2714457168
    AMMO_CAPACITY = 925767036
    ANY_ENERGY_TYPE_COST = 3578062600
    ARC_COST = 3779394102
    ARC_DAMAGE_RESISTANCE = 1546607978
    ARC_ENERGY_CAPACITY = 3625423501
    ASPECT_ENERGY_CAPACITY = 2223994109
    ATTACK = 1480404414
    BLAST_RADIUS = 3614673599
    BOOST = 3017642079
    CHARGE_RATE = 3022301683
    CHARGE_TIME = 2961396640
    DEFENSE = 3897883278
    DISCIPLINE = 1735777505
    DRAW_TIME = 447667954
    DURABILITY = 360359141
    FRAGMENT_COST = 119204074
    GHOST_ENERGY_CAPACITY = 237763788
    GUARD_EFFICIENCY = 2762071195
    GUARD_ENDURANCE = 3736848092
    GUARD_RESISTANCE = 209426660
    HANDICAP = 2341766298
    HANDLING = 943549884
    HEROIC_RESISTANCE = 1546607977
    IMPACT = 4043523819
    INTELLECT = 144602215
    INVENTORY_SIZE = 1931675084
    MAGAZINE = 3871231066
    MOBILITY = 2996146975
    MOD_COST = 514071887
    MOVE_SPEED = 3907551967
    POWER = 1935470627
    POWER_BONUS = 3289069874
    PRECISION_DAMAGE = 3597844532
    RANGE = 1240592695
    RECOIL_DIR = 2715839340
    RECOVERY = 1943323491
    RELOAD = 4188031367
    RESILIENCE = 392767087
    RPM = 4284893193
    SCORE_MULTIPLIER = 2733264856
    SHIELD_DURATION = 1842278586
    SOLAR_COST = 3344745325
    SOLAR_DAMAGE_RESISTANCE = 1546607979
    SOLAR_ENERGY_CAPACITY = 2018193158
    SPEED = 1501155019
    STABILITY = 155624089
    STASIS_COST_3950461274 = 3950461274
    STASIS_COST_998798867 = 998798867
    STRENGTH = 4244567218
    SWING_SPEED = 2837207746
    TIME_TO_AIM_DOWN_SIGHTS = 3988418950
    VELOCITY = 2523465841
    VOID_COST = 2399985800
    VOID_DAMAGE_RESISTANCE = 1546607980
    VOID_ENERGY_CAPACITY = 16120457
    ZOOM = 3555269338
    UNKNOWN = 0

    @staticmethod
    def hashToEnum(_hash: int):
        return StatHashes._value2member_map_.get(_hash, StatHashes.UNKNOWN)

    @staticmethod
    def isWeaponStat(_enum):
        weaponStats = [
            StatHashes.ACCURACY,
            StatHashes.AIMASSIST,
            StatHashes.AIRBORNE,
            StatHashes.AMMO_CAPACITY,
            StatHashes.ZOOM,
            StatHashes.RANGE,
            StatHashes.STABILITY,
            StatHashes.RELOAD,
            StatHashes.MAGAZINE,
            StatHashes.HANDLING,
            StatHashes.VELOCITY,
            StatHashes.BLAST_RADIUS,
            StatHashes.CHARGE_TIME,
            StatHashes.INVENTORY_SIZE,
            StatHashes.RECOIL_DIR,
            StatHashes.RPM,
            StatHashes.GUARD_EFFICIENCY,
            StatHashes.GUARD_ENDURANCE,
            StatHashes.GUARD_RESISTANCE,
            StatHashes.DRAW_TIME,
            StatHashes.SWING_SPEED,
            StatHashes.SHIELD_DURATION,
            StatHashes.IMPACT,
            StatHashes.CHARGE_RATE
        ]
        return _enum in weaponStats


class sockets(Enum):
    INTRINSIC = 395612580
    WEAPON_PERKS = 4241085061
    WEAPON_MODS = 2685412949

    @staticmethod
    def hashToEnum(_hash: int):
        return sockets._value2member_map_[_hash]

    @staticmethod
    def isWeaponSocket(_hash: int):
        return _hash == sockets.WEAPON_PERKS.value
