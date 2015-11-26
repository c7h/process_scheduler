__author__ = 'c7h'

import unittest

from strategy.simple import FiFo, RoundRobin
from strategy.simple import SimpleStrategy
from strategy.multilevel import MLsecondFiFo, MLsecondRR

from scheduler.core import Scheduler, Scheduler
from scheduler.core import SchedulerFactory
from scheduler.timer import SystemTimer

from process.state import State
from process.workplan import Workplan
from process.process import Process, PCB
from process.manager import ProcessManager


class FiFoStubStrategy(SimpleStrategy):
    def __init__(self):
        """
        This is a Fake Fifo strategy
        The concrete schedulers are not yet implemented, so we need this mockup.
        """


    def schedule(self, scheduler):
        """
        FiFo strategies will always return the first process in a queue
        """
        if scheduler.cpu.running_process:
            return scheduler.cpu.running_process
        else:
            try:
                return scheduler.ready_queue.pop()
            except:
                return None


    def addToReadyQueue(self, scheduler, pcb):
        scheduler.ready_queue.append(pcb)



class ConcreteSchedulerCase(unittest.TestCase):
    def test_BasisScheduler_FiFo(self):
        strategy = FiFo()
        scheduler = Scheduler(strategy)
        self.assertIsInstance(scheduler, Scheduler)


    def test_BasisSchedler_FiFo_manyargs(self):
        # swallow too many args without notification
        strategy = FiFo(10, 4, 10, 10, 10, 10)
        scheduler = Scheduler(strategy)
        self.assertIsInstance(scheduler, Scheduler)

    def test_BasisScheduler_RR(self):
        scheduler = Scheduler(RoundRobin(timeslice=10, quantum=4))
        self.assertIsInstance(scheduler, Scheduler)


    def test_BasisScheduler_MLsndFiFo(self):
        scheduler = Scheduler(MLsecondRR(timeslice=10, quantum=4))
        self.assertIsInstance(scheduler, Scheduler)


class RunScheduler(unittest.TestCase):
    """
    Test base scheduler scheduling strategy.
    """

    def setUp(self):
        process2 = Process('02')
        process2.workplan = Workplan().work(90)
        self.pcb2 = PCB(process2, state=State.I)

        process1 = Process('01')
        process1.workplan = Workplan().work(10).launch('02').wait(20).work(10)

        self.pcb1 = PCB(process1, state=State.B)


    def test_scheduler_01(self):
        """If we schedule PCB02 only, it should terminate after 90ms"""
        scheduler = Scheduler(FiFoStubStrategy())
        scheduler.initialize('02')
        scheduler.run()
        self.assertEqual(SystemTimer().timecounter, 90)

    def test_scheduler_02(self):
        """Scheduling terminates at 110ms"""
        scheduler = Scheduler(FiFoStubStrategy())
        scheduler.initialize('01')
        scheduler.run()
        self.assertEqual(SystemTimer().timecounter, 110)


    def test_append_to_queue(self):
        scheduler = Scheduler(FiFoStubStrategy())
        scheduler.addToReadyQueue(self.pcb1)  # process form state inactive get's ready
        scheduler.addToReadyQueue(self.pcb2)  # and now process 2

        self.assertListEqual([self.pcb1, self.pcb2], scheduler.ready_queue)

    def test_get_from_ready_queue(self):
        scheduler = Scheduler(FiFoStubStrategy())
        scheduler.addToReadyQueue(self.pcb2)

        process = scheduler.popFromReadyQueue()
        self.assertEqual(id(process), id(self.pcb2))

    def test_time_since_last_dispatch(self):
        scheduler = Scheduler(FiFoStubStrategy())
        scheduler.addToReadyQueue(self.pcb2)

    def tearDown(self):
        # cleanup process manager instances
        ProcessManager._drop()

class SchedulerNewTestCase(unittest.TestCase):
    def setUp(self):
        process2 = Process('02')
        process2.workplan = Workplan().work(90)
        self.pcb2 = PCB(process2, state=State.I)

        process1 = Process('01')
        process1.workplan = Workplan().launch('02').wait(20).work(10)

        self.pcb1 = PCB(process1, state=State.B)

        self.scheduler = Scheduler(FiFoStubStrategy())

    def test_append_to_matching_queue_01(self):
        # test the processed get added to the right queues.
        self.pcb2.process.name = 'test_q_02'
        self.scheduler.addToMatchingQueue(self.pcb2)
        self.assertListEqual(self.scheduler.ready_queue, [self.pcb2])  # process should be in ready queue

    def test_append_to_matching_queue_02(self):
        # this time with launch section:
        self.scheduler.addToMatchingQueue(self.pcb1)  # first section is a launch(pcb2), add pcb2 to ready_queue
        self.assertListEqual(self.scheduler.ready_queue, [self.pcb2])

    def test_append_to_matching_queue_03(self):
        # process with empty workplan
        pcbX = PCB(Process("X"))
        self.assertRaises(IndexError, self.scheduler.addToMatchingQueue, pcbX)

    def test_append_to_matching_queue_04(self):
        # waiting section
        pcbX = PCB(Process("Wa_pro"))
        pcbX.process.workplan = Workplan().work(15).wait(20)
        pcbX.setReady()
        pcbX.process.doWork(15)  # get rid of work section       <--------|
        pcbX.setRunning()  # <- this should be done during scheduling --|
        self.scheduler.addToMatchingQueue(pcbX)
        self.assertListEqual(self.scheduler.ea_queues[0].queue, [pcbX])

    def test_scheduler_initialize_01(self):
        self.scheduler.initialize('01')
        self.scheduler.run()
        self.assertEqual(self.scheduler.cpu.running_process, None)
        # p1 section 1 is launch(02): should launch 02


    def test_scheduler_run_01(self):
        self.scheduler.initialize(self.pcb1.process.name)
        self.scheduler.run()

    def tearDown(self):
        ProcessManager._drop()



class SchedulerNormalTestCase(unittest.TestCase):
    def setUp(self):
        a = PCB(Process("A"))
        a.process.workplan = Workplan().work(10).wait(10).work(10)

    def testRun_01(self):
        scheduler = Scheduler(FiFoStubStrategy())
        scheduler.initialize("A")
        print 'run normal run 1...'
        scheduler.run()
        process = ProcessManager().getProcessByName("A")
        self.assertEqual(process.state, State.I)

    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()


class FactoryTestCase(unittest.TestCase):
    def test_factory_01(self):
        fifo_scheduler = SchedulerFactory.getScheduler('FiFo')
        self.assertIsInstance(fifo_scheduler, Scheduler)

    def test_factory_02(self):
        ml_snd_RR = SchedulerFactory.getScheduler('MLsecondRR', timeslice=20, quantum=2)
        self.assertIsInstance(ml_snd_RR, Scheduler,
                              'exptected type %s, got an instance of type %s instead'
                              % (Scheduler, type(ml_snd_RR))
        )

    def test_factory_possible_choices(self):
        choices = SchedulerFactory.getPossibleChoices()
        print choices
        self.assertIn('FiFo'.lower(), choices)


if __name__ == '__main__':
    unittest.main()
