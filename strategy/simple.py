__author__ = 'Christoph Gerneth'

from strategy import SimpleStrategy


class FiFo(SimpleStrategy):

    def addToReadyQueue(self, scheduler, pcb):
        queue = scheduler.ready_queue
        pcb.setReady() # you can set to ready, but it's not necessary. the scheduler does it for you
        return queue.append(pcb)

    def schedule(self, scheduler):
        """
        perform a schedule-step
        :return boolean: decision for another run or not?
        """
        ready_process = scheduler.popFromReadyQueue()
        ready_process.process.work()
        return True


class RoundRobin(SimpleStrategy):
    def __init__(self, timeslice, quantum):
        # check type of quantum and timeslice because these are user interfaces
        assert isinstance(timeslice, int)
        assert isinstance(quantum, int)
        #set configuration of the strategy
        self.timeslice = timeslice
        self.quantum = quantum

    def schedule(self):
        return True