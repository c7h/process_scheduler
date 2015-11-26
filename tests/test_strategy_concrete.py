import unittest
from strategy.simple import FiFo
from scheduler.core import Scheduler
from process.process import Process, Workplan, PCB
from process.manager import ProcessManager


class FiFoStrateyTestCase(unittest.TestCase):
    """
    expected result:
    Foo|--  --
    Bar|  --
       0  10  30
    """
    def setUp(self):
        strategy = FiFo()
        self.scheduler = Scheduler(strategy=strategy)
        #we need a simple workplan in the scheduler
        p1 = Process("FOO")
        p2 = Process("BAR")
        self.pcb1 = PCB(p1)
        self.pcb2 = PCB(p2)
        p2.workplan = Workplan().work(10)
        p1.workplan = Workplan().work(10).launch('BAR').work(10)

        self.scheduler.initialize("FOO")

    def test_function01(self):
        self.scheduler.run()

    def tearDown(self):
        ProcessManager._drop()


if __name__ == '__main__':
    unittest.main()
