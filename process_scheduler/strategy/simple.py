__author__ = 'Christoph Gerneth'
from process_scheduler.common.evaluator import ProcessEvaluator
from strategy import SimpleStrategy

class FiFo(SimpleStrategy):
    def addToReadyQueue(self, scheduler, pcb):
        """
        FiFo strategy appends a process at the end of the schedulers ready queue
        """
        scheduler.ready_queue.append(pcb)

    def schedule(self, scheduler):
        """
        FiFo strategies will always return the first process in a queue.
        But since they are non-preemtive, only if there isn't a running process blocking the CPU
        """
        if scheduler.cpu.running_process:
            return scheduler.cpu.running_process
        else:
            try:
                return scheduler.ready_queue.pop()
            except:
                return None

class ShortesJobFirst(FiFo):

    def __calculate_left_work(self, pcb):
        """
        we have to find out how much cpu-time is left in the workplan
        :param pcb: the PCB of the target Process
        :return: int. left service time
        """
        pe = ProcessEvaluator() # we 'abuse' the process evaluator
        # @TODO: change this. The evaluator module is not meant to be used this way
        service_time = pe.getServiceTime(pcb)
        return service_time


    def addToReadyQueue(self, scheduler, pcb):
        """
        Shortes Job First will sort the ready queue by remaining job lenght
        :param scheduler: Scheduler
        :param pcb: PCB to be added
        """
        left_duration =  self.__calculate_left_work(pcb)
        queue = scheduler.ready_queue
        index = len(queue)
        for pcb_elem in queue:
            if self.__calculate_left_work(pcb_elem) < left_duration :
                # job lenght is lower than target => end of targets sub-queue
                index = queue.index(pcb_elem)
                break
        queue.insert(index, pcb)



class RoundRobin(SimpleStrategy):
    def __init__(self, timeslice, quantum):
        # check type of quantum and timeslice because these are user interfaces
        assert isinstance(timeslice, int)
        assert isinstance(quantum, int)
        # set configuration of the strategy
        self.timeslice = timeslice
        self.quantum = quantum

    def schedule(self, scheduler):
        """
        If there is at least one process in the ready queue, the first process from this queue will be scheduled
        :param scheduler: the core scheduler. provides api access to everything you need for scheduling
        :return: PCB or None
        """
        running = scheduler.cpu.running_process
        running_quantum = running.quantum
        if running_quantum > 0:
            # the running pcb still has quantum left. Therefore it is allowed to keep the CPU
            return running
        if len(scheduler.ready_queue) > 0:
            return scheduler.ready_queue.pop(0)  # removes first pcb from ready queue and returns it
        else:
            return None

    def addToReadyQueue(self, scheduler, pcb):
        """
        processes are added at the end of the ready queue (Eduard Glatz. - Operating Systems p. 152)
        :param scheduler: access to the ready queue and more....
        :param pcb: PCB to be added to ready queue
        :return: nothing
        """
        scheduler.ready_queue.append(pcb)
