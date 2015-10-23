__author__ = 'christoph gerneth'

import unittest
from process.state import State
from process.process import PCB, Process
from process.workplan import Workplan
from process.manager import ProcessManager
from scheduler.resource import CPU, EAQueue

from scheduler.timer import SystemTimer


class TestCPUCase(unittest.TestCase):
    def setUp(self):
        # create a list of 10 PCBs
        self.pcbs = [PCB(Process()) for i in range(10)]


    def test_instanciate(self):
        cpu = CPU()
        self.assertIsInstance(cpu, CPU)

    def test_dispatch_01(self):
        p1 = PCB(Process())
        cpu = CPU()
        p1.setReady() # change state from inactive to ready
        old_process = cpu.dispatch(p1)
        # because p1 is our first process, we assume that the old process is none
        self.assertIsInstance(old_process, type(None))

    def test_dispatch_02(self):
        """
        do ten dispatches and check if the last process is the running one
        :return:
        """
        cpu = CPU()
        for pcb in self.pcbs:
            pcb.setReady()
            returning_pcb = cpu.dispatch(pcb)

            if isinstance(returning_pcb,PCB):
                returning_pcb.setInactive()
            else:
                #first process in cpu is None, because it is uninitialized
                pass

        self.assertEqual(cpu.running_process, self.pcbs[-1])

    def test_dispatchCounter(self):
        cpu = CPU()
        for pcb in self.pcbs:
            pcb.setReady()
            cpu.dispatch(pcb)  # dispatch ten times
        self.assertEqual(cpu.dispatch_counter, 10)

    def test_time_since_dispatch_01(self):
        cpu = CPU()
        a_ready_pcb = self.pcbs.pop().setReady()
        cpu.dispatch(pcb=a_ready_pcb)
        SystemTimer().tick()
        SystemTimer().tick()
        self.assertEqual(cpu.time_since_dispatch, 20)

    def test_time_since_dispatch_02(self):
        """now we do 10 dispatches a 20ms"""
        cpu = CPU()
        p1 = self.pcbs.pop().setReady()
        p2 = self.pcbs.pop().setReady()

        time_0 = cpu.time_since_dispatch
        #let it work 10s
        cpu.dispatch(p1)
        SystemTimer().tick()
        time_1 = cpu.time_since_dispatch
        #and now 20
        cpu.dispatch(p2)
        SystemTimer().tick()
        SystemTimer().tick()
        time_2 = cpu.time_since_dispatch

        self.assertEqual(time_1, 10)
        self.assertEqual(time_2, 20)

    def tearDown(self):
        #clean all processes
        ProcessManager._drop()
        SystemTimer._drop()


class EAQueueTestCase(unittest.TestCase):
    def setUp(self):
        #SystemTimer._drop() # just to be sure there is no old timer instance left
        self.st = SystemTimer(10)
        self.queue = EAQueue()
        self.pcbs = (
            PCB(Process("A"), state=State.L), #they need to be in state L or W
            PCB(Process("B"), state=State.W)
        )

    def test_appendToQueue(self):
        """
        append processes and check status after appending:
        """
        for p in self.pcbs:
            self.queue.append(p)

        processes = self.queue.processes
        for i in processes:
            #every process should be in state B
            self.assertTrue(i.state, State.B)

    def test_work_in_append_queue(self):
        """
        after a schedule step is done, we decrease the wait time on every waiting section
        """
        p = PCB(Process("P"), state=State.L)
        p.process.workplan = Workplan().work(10).wait(20)
        p.process.doWork() # get rid of the work section
        self.queue.append(p)

        #and now tick
        st = SystemTimer(timeunit=10)
        st.tick() # tick will trigger a process.work() on every waiting process
        #p.process.work(10)
        for p in self.queue:
            # 10 waits should be left...
            self.assertEqual(p.process.workplan.pop().duration, 10)

    def test_notify(self):
        p = PCB(Process("Res_notify"), state=State.L)
        print ProcessManager().jobs

        p.process.workplan = Workplan().work(20).wait(15).work(25)
        p.process.doWork(20) # get rid of work section
        p.setWaiting()

        #wait(15) in queue
        self.queue.append(p)

        st = SystemTimer(timeunit=10)
        st.tick() #wait(5) left
        self.assertListEqual(self.queue.pickup_ready_processes(), [])
        st.tick() #should tick 5
        # process should be in queue
        ready_p_from_queue = self.queue.pickup_ready_processes()
        self.assertListEqual(ready_p_from_queue, [p])


    def tearDown(self):
        ProcessManager._drop()
        SystemTimer._drop()


if __name__ == '__main__':
    unittest.main()
