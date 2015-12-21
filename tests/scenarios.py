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


class MLScenario1(unittest.TestCase):
    """
    A(1):Work(10),Launch(B),Work(10)
    B(2):Work(10),Launch(C),Work(10)
    C(3):Work(10),Launch(D),Work(10)
    D(4):Work(10),Launch(E),Work(10)
    E(5):Work(10),Launch(F),Work(10)
    F(6):Work(10)

    should result in a funny scenario!
    (here: MLsndFiFo)

    A(1):--                  --
    B(2):  --              --
    C(3):    --          --
    D(4):      --      --
    E(5):        --  --
    F(6):          --
    """

    def setUp(self):
        names = ['F', 'E', 'D', 'C', 'B', 'A']
        prios = [6, 5, 4, 3, 2, 1]
        former_pcb = None
        for n, p in zip(names, prios):
            process = Process(name=n)
            pcb = PCB(process, prio=p)
            if former_pcb != None:
                wp = Workplan().work(10).launch(former_pcb)
            else:
                wp = Workplan().work(10)  # last workplan does't need to launch a pcb
            pcb.process.workplan = wp

    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()
