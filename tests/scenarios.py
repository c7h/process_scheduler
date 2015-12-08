import unittest

from process.manager import ProcessManager
from process.process import Process, PCB, Workplan
from scheduler.timer import SystemTimer
from scheduler.core import SchedulerFactory

# Scenario collections for unittests

class BaseScenario(unittest.TestCase):
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


class SimpleFiFoScenario(unittest.TestCase):
    def setUp(self):
        p1 = Process("A")
        p2 = Process("B")
        self.pcb1 = PCB(p1)
        self.pcb2 = PCB(p2)
        p2.workplan = Workplan().work(10)
        p1.workplan = Workplan().work(10).launch('B').wait(15).work(10)


    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()


class FiFoScenario2(unittest.TestCase):
    def setUp(self):
        pcb1 = PCB(Process("A"))
        pcb2 = PCB(Process("B"))
        pcb1.process.workplan = Workplan().work(10).launch("B").work(10).wait(10).work(5)
        pcb2.process.workplan = Workplan().work(15)

    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()
