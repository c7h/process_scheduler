__author__ = 'christoph gerneth'

import unittest

from process_scheduler.process.process import Process, PCB, State
from process_scheduler.process.manager import ProcessManager
from process_scheduler.process.workplan import Workplan, Launch
from process_scheduler.common.types import ProcessTerminatedMessage
from process_scheduler.scheduler.timer import SystemTimer


class ProcessCase(unittest.TestCase):
    def test_process_randname(self):
        procs = []
        for i in range(10):
            p = Process()
            procs.append(p)
        print procs

    def test_generate_unique_name(self):
        p = Process()
        names = []
        duplette = False
        for i in xrange(1000):
            # test uniqueness...
            # (unsave, because can work 1000 times and
            # fail at the 1001st attempt)
            uname = p._unique_name()
            if uname in names:
                duplette = True
                break
            names.append(uname)
        self.assertFalse(duplette, "Unique-Test failed!")



class PCBCase(unittest.TestCase):
    def setUp(self):
        # generate a list of 10 processes
        self.processes = [Process(name=str(i)) for i in range(10)]

    def test_set_state_01(self):
        lp = PCB(Process('Laufender Prozess'))
        lp.state = State.B
        self.assertEqual(lp.state, State.B)

    def test_pcb_create(self):
        p = PCB(Process())
        self.assertIsInstance(p, PCB)

    def test_pcb_prio_type(self):
        self.assertRaises(AssertionError, PCB, self.processes[0], 'wrong_priority_type')

    def test_decrease_quantum_01(self):
        p = PCB(self.processes.pop(), quantum=10)
        p.decrease_quantum(10)
        self.assertEqual(p.quantum, 0)

    def test_decrease_quantum_02(self):
        p = PCB(self.processes.pop(), quantum=10)
        self.assertRaises(ValueError, p.decrease_quantum, 11)


    def tearDown(self):
        ProcessManager._drop()


class DoWorkCase(unittest.TestCase):
    def setUp(self):
        self.processes = [Process("A"), Process("B")]


    def test_work_01(self):
        # they need a workplan first...
        p1 = self.processes.pop()
        p1.workplan = Workplan().work(15).wait(15)
        print "Workplan before run:", p1.workplan, "History:", p1.history
        p1.doWork(10)
        # get element form workplan
        workplan_element = p1.workplan.plan[0]
        # 10 done - 5 left...
        print "Workplan after 10ms:", p1.workplan, "History:", p1.history
        self.assertEqual(workplan_element.duration, 5,
                         "expected time left in section is %i, but was %i"
                         % (5, workplan_element.duration)
                         )

    def test_work_02(self):
        PCB(Process("B"))
        w1 = Workplan().launch("B").work(30)
        p1 = PCB(Process("A"))
        p1.process.workplan = w1

        print "Workplan before run:", p1.process.workplan, "History:", p1.process.history
        p1.process.doWork(20)
        print "Workplan after 10ms:", p1.process.workplan, "History:", p1.process.history

        # should launch and work 20 of work section
        self.assertIsInstance(p1.process.history.plan[0], Launch)
        self.assertTrue(p1.process.history.plan[-1].duration == 20)

    def test_work_03(self):
        """work 20ms with a 10ms Section should return after 10ms"""
        PCB(Process("B"))

        w1 = Workplan().work(10)
        p1 = PCB(Process("A"))
        p1.process.workplan = w1

        print "Workplan before run:", p1.process.workplan, "History:", p1.process.history
        try:
            p1.process.doWork(20)  # now we run 20 ms...
        except ProcessTerminatedMessage:
            print "process terminated:", p1.process.history
        print "Workplan after 20ms:", p1.process.workplan, "History:", p1.process.history

        # should work 10ms and then return.
        duration = p1.process.history.plan[0].duration
        self.assertTrue(duration == 10, "expected 10ms, got %i" % duration)

    def test_work_04(self):
        """
        if no time to work is provided, work one section (plus action section)
        """
        PCB(Process("B"))
        p1 = PCB(Process("A"))
        p1.process.workplan = Workplan().work(30).launch('B').wait(10).work(10)

        print "Workplan before run:", p1.process.workplan, "History:", p1.process.history
        step_counter = 0
        wp_len = len(p1.process.workplan.plan)
        print "there are", wp_len, "sections in the workplan"
        for i in xrange(wp_len):
            worked_time = p1.process.doWork()
            print 'step done...'
            step_counter += 1

        print "Workplan after:", p1.process.workplan, "History:", p1.process.history
        self.assertEqual(step_counter, 4, "not enought steps done: [%i/%i]" % (step_counter, 4))

    @unittest.skip("we don't use launch-execution after work section anymore")
    def test_work_launch(self):
        """include launch-section at the end"""
        p = Process("work_launch_process")
        b = Process("process_to_launch")
        p.workplan = Workplan().work(10).launch(b).work(10)

        p.doWork(10)

        self.assertEqual(p.workplan, Workplan().work(10))
        self.assertEqual(p.history, Workplan().work(10).launch(b))


    def test_process_terminated_01(self):
        p1 = Process("I_will_terminate")
        p1.workplan = Workplan().work(12)

        p1.doWork(10)
        self.assertRaises(ProcessTerminatedMessage, p1.doWork, 10)

    def test_process_terminated_02(self):
        p1 = Process("I_will_terminate")
        p1.workplan = Workplan().work(2)

        try:
            p1.doWork(10)
        except ProcessTerminatedMessage as e:
            last_section_length = e.last_section.duration
        self.assertEqual(last_section_length, 2)


    def tearDown(self):
        ProcessManager._drop()


class ProcessManagerCase(unittest.TestCase):
    def setUp(self):
        self.pm = ProcessManager()
        self.pm.jobs = []  # make sure to work with clean job-queue

    def test_getProcessByName_01(self):
        aprocess = PCB(Process('1'))
        bprocess = PCB(Process('2'))
        print self.pm.jobs

    def test_registerProcess(self):
        # pcb should register itself at creation-time
        aprocess = PCB(Process('X'))
        getit = self.pm.getProcessByName('X')
        self.assertEqual(aprocess, getit)

    def test_registerProcess_02(self):
        # assert raise when you try to register an already known process name
        PCB(Process('F'))
        b = Process('F')
        self.assertRaises(ValueError, PCB, b)

    def test_getActiveProcess_01(self):
        # non-failure test. one running process
        PCB(Process('X'), state=State.L)
        PCB(Process('Y'), state=State.I)

        active_p = self.pm.getActiveProcess()
        self.assertEqual(active_p.state, State.L)

    def test_getActiveProcess_02(self):
        # no running process should raise IndexError
        self.assertRaises(IndexError, self.pm.getActiveProcess)

    def test_getActiveProcess_03(self):
        # two active processes should raise RuntimeError
        PCB(Process("A"), state=State.L)
        PCB(Process("B"), state=State.L)
        self.assertRaises(RuntimeError, self.pm.getActiveProcess)

    def tearDown(self):
        # clear job queue at the end (for security reasons)
        ProcessManager._drop()


if __name__ == '__main__':
    unittest.main()
