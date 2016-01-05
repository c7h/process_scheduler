__author__ = 'c7h'

from strategy import MultiLevelStrategy
from simple import FiFo, RoundRobin


class MLsecondFiFo(MultiLevelStrategy):
    def __init__(self):
        self.secondaryStrategy = FiFo()

    def schedule(self, scheduler):
        """
        in MLsndFiFo, the FiFo's scheduling strategy is used to make scheduling decisions
        :param scheduler: Scheduler
        :return:
        """
        active = scheduler.cpu.running_process
        try:
            possible_next = scheduler.ready_queue[-1]
        except IndexError:
            # ready queue is empty => reschedule
            return active

        if active.priority < possible_next.priority:
            # if active priority lower than possible next:
            scheduler.ready_queue.remove(possible_next)
            decision = possible_next
            return decision

    def addToReadyQueue(self, scheduler, pcb):
        """
        now we have a multilevel ready queue. we need to add the process according to it's priority.
        :param scheduler:
        :param pcb: the PCB to be added
        """
        queue = scheduler.ready_queue

        # append pcb at the end of the priority sublist
        index = len(queue)
        for process in queue:
            if process.priority < pcb.priority:
                # priority is lower than target => end of targets sub-queue
                index = queue.index(process)
                break

        queue.insert(index, pcb)


class MLsecondRR(MultiLevelStrategy):
    def __init__(self, timeslice, quantum):
        self.secondaryStrategy = RoundRobin(timeslice, quantum)

    def schedule(self):
        return True
