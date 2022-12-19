import unittest
from Weapons import rpmToDelay



from util.DpsCalc import calcDPS, calcRefund
from util.TtkCalc import calcTtk
#make a test for calcDPS
class TestCalcDPS(unittest.TestCase):

    def setUp(self) -> None:
        #dps stuff
        self.dps_rof = 600
        self.dps_dmg = 1_000
        self.dps_critMult = 1.5
        self.dps_reload = 1
        self.dps_magSize = 3
        self.dps_reserves = 10
        self.dps_isChargeTime = False
        #refund stuff
        self.ref_refunds = [{"CRIT":True,"REQUIREMENT":3,"REFUND":1}]#,{"CRIT":False,"REQUIREMENT":4,"REFUND":1}
        self.ref_magSize = 7
        self.ref_critsMissed = 0
        #ttk stuff
        self.ttk_rof = 150
        self.ttk_resilience = 6
        self.ttk_dmg = 47
        self.ttk_critMult = 1.5
        self.ttk_magSize = 11

    def test_calcDPS(self):
        _return = calcDPS(rpmToDelay(self.dps_rof),self.dps_dmg,self.dps_critMult,self.dps_reload,self.dps_magSize,self.dps_reserves,self.dps_isChargeTime)
        self.assertEqual(_return, [22500.0, 6428.571428571429, 5192.307692307692, 4166.666666666667], "calcDPS is not working correctly")

    def test_calcRefund(self):
        _return = calcRefund(self.ref_magSize,self.ref_critsMissed,self.ref_refunds)
        self.assertEqual(_return, 10, "calcRefund is not working correctly")

    def test_calcTtk(self):
        _return = calcTtk(rpmToDelay(self.ttk_rof),self.ttk_resilience,self.ttk_dmg,self.ttk_critMult,self.ttk_magSize)
        self.assertEqual(_return, {"ShotsNeeded": 3,"Optimal TtK": 0.8,"Crit Percent": 1.0,"Bodyshot Ttk": 1.6}, "calcTtk is not working correctly")