__author__ = 'Christoph Gerneth'
import sys
from strategy.strategy import Strategy
from timer import TimerListener, SystemTimer
from resource import CPU, EAQueue
from process.manager import ProcessManager
from process.workplan import Work, Wait, Launch, Ready
# imports used by Factory:
from strategy.simple import FiFo, RoundRobin
from strategy.multilevel import MLsecondRR, MLsecondFiFo

# endless recursion prevention
# actually there is a built-in recursion break provided by the python runtime environment:
sys.setrecursionlimit(1000)


class Scheduler(TimerListener):
    def __init__(self, strategy):
        assert isinstance(strategy, Strategy)
        self.howToSchedule = strategy

        # timer listeners
        self.cpu = CPU()  # that's what we want to manage
        self.processManager = ProcessManager()  # is responsible for managing processes
        self.ea_queues = [EAQueue()] * 1
        self.ready_queue = list()  # hold only processes waiting for the cpu
        self.init_process = None  # you have to initialize the scheduler first

        self._loop_counter = 0  # count how many time the run-method was called

        # every process needs the same quantum at beginning of the run
        try:
            self.quantum = strategy.__getattribute__("quantum")
        except AttributeError:
            self.quantum = 4
        self.processManager.setQuantumForEveryProcess(
            self.quantum)  # TODO:move to run-method / assuming here: processes are created before scheduler instantiates

        try:
            self.timeslice = strategy.__getattribute__("timeslice")  # make timeslice public
        except AttributeError:
            self.timeslice = 10

        SystemTimer().timeunit = self.timeslice
        SystemTimer().register(self)  # register at system clock

    def popFromReadyQueue(self):
        """
        get the next process from the ready queue. The state belongs in state ready. I
        :return: PCB
        """
        try:
            return self.ready_queue.pop(0)
        except IndexError:
            raise IndexError("the schedulers ready queue is empty")

    def addToEAQueue(self, pcb, i=0):
        print "add process to EAQueue%i %s" % (i, pcb)
        self.ea_queues[i].append(pcb)

    def notify(self, timestamp):
        """an event occurred. On every event, we have to decide if we dispatch the running process or not"""
        print "Scheduler notified after a step of", timestamp
        if self.schedule():
            # there is still something to do
            SystemTimer().tick()
        else:
            print "FINISHED"

    def initialize(self, start_pcb_str):
        """
        initialize the scheduler by defining the first process to run.
        :param start_pcb_str: name of the initial process
        """
        self.init_process = self.processManager.getProcessByName(start_pcb_str)

    def run(self):
        """
        start the scheduler
        begin with initialisation of the ready queue
        :return:
        """
        if self.init_process is None:
            raise RuntimeError("No init process found! please initialise first")
        else:
            # on the first run, the initial process is pushed to the ready queue
            self.addToMatchingQueue(self.init_process)  # init fill the ready queue

        self.schedule()
        # init process is now in CPU, time is 0
        SystemTimer().tick()  # do the first tick

    def addToMatchingQueue(self, pcb):
        """
        append pcb to right queue
        there are two types of queue: ready queues and waiting queues (aka. EAQueues)
        :param pcb: pcb to push to queue
        :return:
        :raise IndexError: if pcb's Workplan is empty
        """
        if isinstance(pcb.process.workplan.head(), Wait):
            # waiting section means ea queue:
            self.addToEAQueue(pcb)
        elif isinstance(pcb.process.workplan.head(), Work):
            self.addToReadyQueue(pcb)
        elif isinstance(pcb.process.workplan.head(), Launch):
            # interesting! now we have a launch. We push the Included process to the queue!
            print "trying to launch", pcb.process.workplan.head().action
            self.addToMatchingQueue(pcb.process.workplan.head().action)  # the process to launch is stored in the action
        else:
            # these sections are not made for queues
            pass

    def schedule(self):

        # check the ea queues if there are finished processes. if so, append them to the queues
        finished_waiting_processes = self.__check_ea_queues()
        for p in finished_waiting_processes:
            self.addToMatchingQueue(p)

        # active = self.processManager.getActiveProcess()
        active = self.cpu.running_process

        try:
            next_section = active.process.workplan.head()
        except:
            pass
        else:
            if isinstance(next_section, Wait):
                # process will enter wait section: dispatch
                try:
                    next_from_ready_queue = self.ready_queue.pop()
                except IndexError:
                    # ready queue empyt
                    next_from_ready_queue = None
                waiting_pcb = self.cpu.dispatch(next_from_ready_queue)
                self.addToMatchingQueue(waiting_pcb)
                active = self.cpu.running_process  # notwendig, da dispatch ausgefuehrt wurde
            if isinstance(next_section, Launch):
                # process will launch another process
                self.addToMatchingQueue(active)

        # collect information about resources
        sum_waiting_pcbs = sum(map(lambda x: len(x), self.ea_queues))  # Sum of all PCBs in EAQueues
        readyq_empty = True if len(self.ready_queue) == 0 else False  # ready queue empty?

        if not active and readyq_empty:
            # cpu leer, runq leer
            if sum_waiting_pcbs > 0:
                # but there are still waiting processes
                next_run = True
            else:
                next_run = False  # and no more processes in ea_queue
        elif not active and not readyq_empty:
            # cpu leer, runq voll: dispatchen und nochmal laufen
            ready = self.ready_queue.pop()
            ready.refill_quantum()  # refill quantum for next process in cpu
            self.cpu.dispatch(ready)
            # update system timer
            work_duration = ready.process.workplan.head().duration
            SystemTimer().next_tick_in(work_duration)
            next_run = True
        elif active and readyq_empty:
            # cpu voll, runq leer
            # there is no readyq_empty process...
            # reschedule: process in cpu belongs in cpu
            print 'reschedule process'
            if self.cpu.running_process.quantum == 0:
                # quantum gets refilled, if process is allowed to run again and the quantum was already consumed
                self.cpu.running_process.refill_quantum()
            next_run = True
        elif active and not readyq_empty:
            # cpu voll, runq voll
            next_run = True
            if SystemTimer().next_temp_timeunit != 0:
                # we need this distinction because this happens in 2 steps...
                strategy_result = self.howToSchedule.schedule(self)
                if strategy_result is not active:
                    # neuer process
                    old = self.cpu.dispatch(strategy_result)
                    active = strategy_result  # the new active process is the strategy result
                    self.addToMatchingQueue(old)
        else:
            # unefined state
            raise RuntimeError("undefined scheduling state")

        self._loop_counter += 1  # count the scheduling-steps
        return next_run

    def __check_ea_queues(self):
        """
        check if there are finished processes in the queue
        :return list: list of all ready pcbs
        """
        finished_waiting_processes = []
        for ea_q in self.ea_queues:
            p = ea_q.pickup_ready_processes()
            finished_waiting_processes.extend(p)
        return finished_waiting_processes

    def addToReadyQueue(self, pcb):
        """
        add process to ready queue
        :param pcb: pcb to be added
        """
        pcb.setReady()
        self.__maintain_process_history(pcb)
        print "add process to ready queue:", pcb
        # if rescheduled because of time quantum, add at the end, if it's because of preemption, add to the beginning
        self.howToSchedule.addToReadyQueue(scheduler=self, pcb=pcb)
        return True

    def __maintain_process_history(self, pcb):
        """
        usually, the history is maintained in the doWork()-Method in the Process-Class.
        However the Ready-Section must be maintained here.
        The Ready-Section is not part of the regular workplan.
        """
        # if len(pcb.process.history.plan) == 0:
        #     ready_time = 0
        # else:
        #     ready_time = SystemTimer().next_temp_timeunit
        # @TODO: fix this ugly method...
        ready_time = 0
        new_history_section = Ready(ready_time)
        new_history_section.starting_at = SystemTimer().timecounter
        new_history_section.ending_at = SystemTimer().timecounter + ready_time
        pcb.process.history.insert(new_history_section, i=len(pcb.process.history.plan))


class SchedulerFactory(object):
    """
    this is not an Abstract Factory. Instead we use a factory method (GOF:107) here
    to generate the schedulers based on strategies
    """
    __zuordnung = {
        'fifo': FiFo,
        'roundrobin': RoundRobin,
        'mlsecondfifo': MLsecondFiFo,
        'mlsecondrr': MLsecondRR
    }

    @classmethod
    def getPossibleChoices(cls):
        """
        :return: a list of all possible strategy access keys...
        """
        return cls.__zuordnung.keys()

    @classmethod
    def getScheduler(cls, strategy_str, timeslice=10, quantum=4):
        """
        Build a new Scheduler based on the chosen strategy.
        :param strategy_str: string - choose the strategy you want to use for scheduling
        :param timeslice: default timeslice is 10ms
        :param quantum: default quantum is 4
        :return: Scheduler
        :raise: NotImplementedError if the sting cannot be found
        """
        assert isinstance(strategy_str, str)
        for possible, strategy in cls.__zuordnung.iteritems():
            if strategy_str.lower() == possible.lower():
                chosen_strategy = strategy(timeslice, quantum)
                return Scheduler(chosen_strategy)
        raise NotImplementedError("the requested scheduler [%s] could not be found. typo?" % strategy_str)
