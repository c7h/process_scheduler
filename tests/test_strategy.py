__author__ = 'c7h'

import unittest
from strategy.multilevel import MLsecondFiFo
from strategy.simple import FiFo, RoundRobin
from strategy.strategy import Strategy


class TestMeta(unittest.TestCase):
    def test_instantiateMultiLevel_01(self):
        ml_strategy = MLsecondFiFo()
        pass

    def test_call_many_parameters(self):
        #FiFo should work even if i give them quantum and timeslice parameters.
        # It doesn't use it, but should not complain about them
        strategy = FiFo(timeslice=10, quantum=12)
        self.assertIsInstance(strategy,Strategy)


if __name__ == '__main__':
    unittest.main()
