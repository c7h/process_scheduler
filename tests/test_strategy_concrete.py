import unittest
from scenarios import BaseScenario
from scheduler.core import Scheduler
from strategy.simple import FiFo, RoundRobin




class FiFoStrateyTestCase(BaseScenario):
    """
    expected result:
    Foo|----
    Bar|  | --
       0  10  30
    """

    def setUp(self):
        super(FiFoStrateyTestCase, self).setUp()
        strategy = FiFo()
        self.scheduler = Scheduler(strategy=strategy)
        self.scheduler.initialize("FOO")

    def test_function01(self):
        self.scheduler.run()


class RRStrategyTestCase(BaseScenario):
    def setUp(self):
        super(RRStrategyTestCase, self).setUp()
        strategy = RoundRobin(quantum=4, timeslice=10)
        self.scheduler = Scheduler(strategy=strategy)
        self.scheduler.initialize("FOO")

    def test_function01(self):
        self.scheduler.run()


if __name__ == '__main__':
    unittest.main()
