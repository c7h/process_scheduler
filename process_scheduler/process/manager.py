__author__ = 'Christoph Gerneth'
from process_scheduler.common.types import SingletonType
from state import State


class ProcessManager(object):
    """
    The Process Manager is responsible for managing the PCBs.
    It holds records for every Process in a Table-Like structure called PCB.
    The PCB registers at the ProcessManager at creation time. If there is already
    a PCB with a process with the same name, a Value error is raised.
    There is only one Process Manager in the System.
    """
    __metaclass__ = SingletonType

    def __init__(self):
        self.jobs = list()

    def addPCB(self, pcb):
        """
        try to add pcb to the job queue
        :param pcb: PCB to be added
        :return: nothing
        :raises: ValueError if PCB contains a process with the same name
        """
        try:
            pcb = self.getProcessByName(pcb.process.name)
            raise ValueError('Sorry, the process name %s is already taken by %s' % (pcb.process.name, pcb))
        except IndexError:
            # allright, there is no process with this name yet.
            self.jobs.append(pcb)


    def getProcessByName(self, name):
        """
        try to get a PCB identified by the process name
        :param name: name of the process asd string
        :return: PCB containing the process
        :raises: IndexError if process not found
        """
        search_results = filter(lambda p: p.process.name == name, self.jobs)
        try:
            return search_results.pop()
        except IndexError:
            raise IndexError("no such process: %s" % name)

    def getActiveProcess(self):
        """
        Active Processes are Processes in state 'laufend'.
        :raises IndexError: There is no more active process in the job queue
        :raises RuntimeError: There is more than one active process in the queue. Inconsistency
        :return: a PCB in state laufend
        """

        active_candidates = filter(lambda p: p.state == State.L, self.jobs)
        if len(active_candidates) > 1:
            raise RuntimeError('There are %i active processe managed by the ProcessManager. 1 is allowed'
                               % len(active_candidates)
            )
        elif len(active_candidates) == 0:
            raise IndexError('No more active processes')
        else:
            return active_candidates.pop()

    def setQuantumForEveryProcess(self, quantum):
        """
        initially, we want to have every process the same amount of time quantum
        :param quantum: time quantum / int
        :return:
        """
        for p in self.jobs:
            p.quantum_initial = quantum
            p.quantum = quantum