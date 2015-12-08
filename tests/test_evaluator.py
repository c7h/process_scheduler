import unittest
from scenarios import SimpleFiFoScenario, FiFoScenario2

from common.evaluator import ProcessEvaluator, StrategyEvaluator
from process.workplan import Work, Wait, Ready
from scheduler.core import SchedulerFactory




class ProcessEvaluatorTestCase(SimpleFiFoScenario):
    def setUp(self):
        super(ProcessEvaluatorTestCase, self).setUp()
        scheduler = SchedulerFactory.getScheduler("FiFo", timeslice=10)
        scheduler.initialize("A")
        scheduler.run()

        self.evaluator = ProcessEvaluator()

    def test_getPeriodForPCB_01(self):
        # test get pcb by name
        period_B = self.evaluator.getPeriodForPCB("B")
        self.assertTupleEqual(period_B, (10, 20))

    def test_getPeriodForPCB_02(self):
        period_A = self.evaluator.getPeriodForPCB("A")
        self.assertTupleEqual(period_A, (0, 35))

    def test_getPeriodForPCB_03(self):
        # test get pcb by reference
        period_B = self.evaluator.getPeriodForPCB(self.pcb2)
        self.assertTupleEqual(period_B, (10, 20))

    def test_getServiceTime_01(self):
        service_time = self.evaluator.getServiceTime("A")
        self.assertEqual(service_time, 20)

    def test_getServiceTime_02(self):
        service_time = self.evaluator.getServiceTime("B")
        self.assertEqual(service_time, 10)

    def test_getWaitTime_01(self):
        wait_time = self.evaluator.getWaitTime("A")
        self.assertEqual(wait_time, 15)

    def test_getWaitTime_02(self):
        wait_time = self.evaluator.getWaitTime("B")
        self.assertEqual(wait_time, 0)


class StrategyEvaluatorTestCase(SimpleFiFoScenario):
    def setUp(self):
        super(StrategyEvaluatorTestCase, self).setUp()
        scheduler = SchedulerFactory.getScheduler("FiFo", timeslice=10)
        scheduler.initialize("A")
        scheduler.run()

        self.evaluator = StrategyEvaluator()

    def test_averageCPUusage(self):
        expected = 30.0 / 35.0  # remeber: at least one value has to be a float!
        avg_usage = self.evaluator.getAverageCPUusage()
        self.assertEqual(avg_usage, expected)

    def testPeriodDuration(self):
        duration = self.evaluator.getPeriodDuration()
        self.assertEqual(duration, 35)


class StrategyEvaluatorComplexTestCase(FiFoScenario2):
    def setUp(self):
        super(StrategyEvaluatorComplexTestCase, self).setUp()
        scheduler = SchedulerFactory.getScheduler("FiFo", timeslice=10)
        scheduler.initialize("A")
        scheduler.run()
        self.evaluator = ProcessEvaluator()

    def test_getReadySectionsForPCB_01(self):
        # process A got a ready section at 30 - 35 after wait
        # and another at the beginning with duration 0 (process got active)
        ready_secs = self.evaluator._getReadySectionsForPCB("A")
        self.assertListEqual(ready_secs, [Ready(0), Ready(5)])

    def test_getReadySectionsForPCB_02(self):
        # process B got a ready section at 10-20 after launch
        ready_secs = self.evaluator._getReadySectionsForPCB("B")
        self.assertEqual(len(ready_secs), 1)


if __name__ == '__main__':
    unittest.main()
