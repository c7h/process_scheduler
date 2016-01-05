__author__ = 'c7h'

import unittest
from strategy.multilevel import MLsecondFiFo
from strategy.simple import FiFo
from strategy.strategy import Strategy

from scheduler.core import Scheduler
from process.process import PCB, Process
from process.manager import ProcessManager
from scheduler.timer import SystemTimer



class TestMeta(unittest.TestCase):
    def test_instantiateMultiLevel_01(self):
        ml_strategy = MLsecondFiFo()
        self.assertIsInstance(ml_strategy, Strategy)

    def test_call_many_parameters(self):
        # FiFo should work even if i give them quantum and timeslice parameters.
        # It doesn't use it, but should not complain about them
        strategy = FiFo(timeslice=10, quantum=12)
        self.assertIsInstance(strategy, Strategy)

    def test_MLsndFiFo_add_to_ready_queue_01(self):
        strategy = MLsecondFiFo()
        scheduler = Scheduler(strategy=strategy)
        pcb_list = [PCB(Process("A"), prio=3),
                    PCB(Process("B"), prio=9),
                    PCB(Process("C"), prio=2),
                    PCB(Process("D"), prio=8),
                    PCB(Process("E"), prio=3)
                    ]

        for p in pcb_list:
            print "adding %s(%i) to ready queue: %s" % (p.process.name, p.priority, scheduler.ready_queue)
            strategy.addToReadyQueue(scheduler, p)

        resulting_list_names = [x.process.name for x in scheduler.ready_queue]
        print "resulting list is", resulting_list_names
        self.assertListEqual(["B", "D", "A", "E", "C"], resulting_list_names)

    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()

if __name__ == '__main__':
    unittest.main()
