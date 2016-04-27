__author__ = 'c7h'

import unittest

from process_scheduler.process.state import State
#state machine test
from process_scheduler.process.process import PCB, Process
from process_scheduler.process.manager import ProcessManager


class StateCase(unittest.TestCase):
    def test_unique_01(self):
        """
        it would be nice to have only one instance per state
        """
        a, b, c, d = State.I, State.I, State.I, State.I
        self.assertTrue(a is b is c is d)

    def test_representation(self):
        rep = repr(State.L)
        print rep
        self.assertTrue("Laufend".lower() in rep.lower())


class StateMachineCase(unittest.TestCase):
    """
    See Abb.2.2 bachelors thesis Christoph Gerneth 2015 for process state model
    """
    def setUp(self):
        ProcessManager().jobs = [] # make sure the manager is clean
        self.pcb = PCB(Process('state-test'))

    def test_pcb_states_IB(self):
        #process is in state I by default
        self.pcb.setReady()
        pass

    def test_pcb_states_BL(self):
        self.pcb.state = State.B # initialize process
        self.pcb.setRunning()
        pass

    def test_valid_states(self):
        """
        covering all edges of the graph.
        """
        self.pcb.state = State.I # we start with an inactive state
        self.pcb.setReady()   # I -> B
        self.pcb.setRunning() # B -> L
        self.pcb.setWaiting() # L -> W
        self.pcb.setReady()   # W -> B
        self.pcb.setRunning() # B -> L (this needs to be done twice, sorry)
        self.pcb.setInactive()# L -> I

        self.assertIs(self.pcb.state, State.I)

    def test_valid_states_02(self):
        """
        should do nothing...
        """
        self.pcb.state = State.I
        self.pcb.setInactive()
        pass


    def test_invalid_01(self):
        self.pcb.state = State.I
        self.assertRaises(RuntimeError, self.pcb.setRunning)


if __name__ == '__main__':
    unittest.main()