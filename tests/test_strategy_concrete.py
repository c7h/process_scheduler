import unittest
from scenarios import BaseScenario, MLScenario1

from scheduler.core import Scheduler
from strategy.simple import FiFo, RoundRobin
from strategy.multilevel import MLsecondFiFo
from common.evaluator import StrategyEvaluator, ProcessEvaluator


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
        self.se = StrategyEvaluator()
        self.pe = ProcessEvaluator()

    def _run_rr(self, quantum, timeslice):
        strategy = RoundRobin(quantum=quantum, timeslice=timeslice)
        scheduler = Scheduler(strategy=strategy)
        scheduler.initialize("FOO")
        scheduler.run()

    def test_RR_t10_q1(self):
        self._run_rr(quantum=1, timeslice=10)
        start, end = self.pe.getPeriodForPCB("FOO")
        self.assertEqual(end, 30)  # work(10),launch(BAR),ready(10),work(10) -> 30

    def test_RR_t10_q2(self):
        self._run_rr(quantum=2, timeslice=10)
        start, end = self.pe.getPeriodForPCB("FOO")
        self.assertEqual(end, 20)  # work(10),launch(BAR),work(10) -> 20

    def test_RR_t5_q1(self):
        self._run_rr(quantum=1, timeslice=5)
        start, end = self.pe.getPeriodForPCB("BAR")
        self.assertTupleEqual((10, 25), (start, end))

    def test_RR_t5_q2(self):
        self._run_rr(quantum=2, timeslice=5)
        start, end = self.pe.getPeriodForPCB("FOO")
        self.assertTupleEqual((0, 30), (start, end))

class MultilevelPriorityFiFo(MLScenario1):
    def test_MLsndFiFo_01(self):
        strategy = MLsecondFiFo()
        scheduler = Scheduler(strategy=strategy)
        scheduler.initialize("A")
        scheduler.run()


if __name__ == '__main__':
    unittest.main()
