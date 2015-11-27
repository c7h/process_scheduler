import unittest
from scheduler.core import Scheduler
from process.process import Process, Workplan, PCB
from process.manager import ProcessManager
from scheduler.timer import SystemTimer
from strategy.simple import FiFo, RoundRobin


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # we need a simple workplan in the scheduler
        p1 = Process("FOO")
        p2 = Process("BAR")
        self.pcb1 = PCB(p1)
        self.pcb2 = PCB(p2)
        p2.workplan = Workplan().work(10)
        p1.workplan = Workplan().work(10).launch('BAR').work(10)

    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()


class FiFoStrateyTestCase(BaseTestCase):
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


class RRStrategyTestCase(BaseTestCase):
    def setUp(self):
        super(RRStrategyTestCase, self).setUp()
        strategy = RoundRobin(quantum=4, timeslice=10)
        self.scheduler = Scheduler(strategy=strategy)
        self.scheduler.initialize("FOO")

    def test_function01(self):
        self.scheduler.run()


if __name__ == '__main__':
    unittest.main()
