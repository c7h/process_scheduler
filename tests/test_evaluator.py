import unittest
from scenarios import SimpleFiFoScenario, FiFoScenario2

from process_scheduler.common.evaluator import ProcessEvaluator, StrategyEvaluator
from process_scheduler.process.workplan import Work, Wait, Ready
from process_scheduler.scheduler.core import SchedulerFactory


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

    def test_PeriodDuration(self):
        duration = self.evaluator.getPeriodDuration()
        self.assertEqual(duration, 35)

    def test_getMeanResponseTime(self):
        # in this case, the mean response time is 0
        mean_r = self.evaluator.getMeanResponseTime()
        self.assertEqual(mean_r, 0.0)


class ProcessEvaluatorComplexTestCase(FiFoScenario2):
    def setUp(self):
        super(ProcessEvaluatorComplexTestCase, self).setUp()
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

    def test_geResponseTime_01(self):
        response_time = self.evaluator.getResponseTime("A")
        self.assertListEqual([0, 5], response_time)

    def test_geResponseTime_02(self):
        response_time = self.evaluator.getResponseTime("B")
        self.assertListEqual([10], response_time)

    def test_getTurnaroundTime_01(self):
        turnaroundtime = self.evaluator.getTurnaroundTime("A")
        self.assertEqual(turnaroundtime, 35)

    def test_getTurnaroundTime_02(self):
        turnaroundtime = self.evaluator.getTurnaroundTime("B")
        self.assertEqual(turnaroundtime, 15)

    def test_getWaitTime_01(self):
        waittime = self.evaluator.getWaitTime("A")
        self.assertEqual(waittime, 15)

    def test_getWaitTime_02(self):
        waittime = self.evaluator.getWaitTime("B")
        self.assertEqual(waittime, 10)


class StrategyEvaluatorComplexTestCase(FiFoScenario2):
    def setUp(self):
        super(StrategyEvaluatorComplexTestCase, self).setUp()
        scheduler = SchedulerFactory.getScheduler("FiFo", timeslice=10)
        scheduler.initialize("A")
        scheduler.run()

        self.evaluator = StrategyEvaluator()


    def test_getAverageCPUusage(self):
        cpu_usage = self.evaluator.getAverageCPUusage()
        self.assertEqual(cpu_usage, 1.0)

    def test_getPeriodDuration(self):
        periodDuration = self.evaluator.getPeriodDuration()
        self.assertEqual(periodDuration, 40)

    def test_getMeanResponseTime(self):
        meanRT = self.evaluator.getMeanResponseTime()
        self.assertEqual(meanRT, 7.5)

if __name__ == '__main__':
    unittest.main()
