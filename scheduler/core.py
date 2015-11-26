__author__ = 'Christoph Gerneth'
import sys

from strategy.strategy import Strategy
from timer import TimerListener, SystemTimer
from resource import CPU, EAQueue
from process.manager import ProcessManager
from process.workplan import Work, Wait, Launch

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

        #timer listeners
        self.cpu = CPU()  # that's what we want to manage
        self.processManager = ProcessManager()  # is responsible for managing processes
        self.ea_queues = [EAQueue()]*1

        self.ready_queue = list()  # hold only processes waiting for the cpu


        self.init_process = None # you have to initialize the scheduler first

        SystemTimer().register(self)  #register at system clock

        self._loop_counter = 0  # count how many time the run-method was called

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
            #there is still something to do
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
            self.addToMatchingQueue(self.init_process) # init fill the ready queue


        self.schedule()
        #init process is now in CPU, time is 0
        SystemTimer().tick() #do the first tick

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

    def schedule_old(self):
        """
        Generische Arbeitsweise des Schedulers
        :return true if there will be a next run
        """
        next_run = False

        if self.cpu.running_process is None and self._loop_counter == 0:
            # this the initial run
            self.addToMatchingQueue(self.init_process) # init fill the ready queue


        lc = self._loop_counter
        print "RUN %2i" % (self._loop_counter)
        self._loop_counter += 1 # count the scheduling-steps


        #check the ea queues if there are finished processes. if so, append them to the queues
        finished_processes = self.__check_ea_queues()
        for p in finished_processes:
            self.addToMatchingQueue(p) # add to ready queue

        #scheduler, decide if (and what process) we should schedule:
        next_process = self.howToSchedule.schedule(self)



        if self.cpu.running_process:
            # if the running process want to wait, push him to the ea_queue and dispatch
            active_pcb_wp_head = self.cpu.running_process.process.workplan.head()
            if isinstance(active_pcb_wp_head, Wait):  #Trainwreck-Alert!
                wait_pcb = self.cpu.dispatch(next_process)
                self.addToMatchingQueue(wait_pcb)
                next_run = True
            if isinstance(active_pcb_wp_head, Launch):
                # do launch
                launching_pcb = active_pcb_wp_head.action
                self.addToMatchingQueue(launching_pcb)



        # decide what to do with the next_process:
        if not self.cpu.running_process and not next_process:
            # cpu leer, runq leer
            # no more jobs to do, terminated
            print "Scheduler finished"
            next_run = False
        elif not self.cpu.running_process and next_process:
            # cpu leer, runq voll :scheduling decision was to switch context :)
            # the cpu is free and there is a ready process:
            self.cpu.dispatch(next_process)
            next_run = True
        elif self.cpu.running_process and not next_process:
            # cpu voll, runq leer
            # there is no next process...
            # reschedule: process in cpu belongs in cpu
            next_run = True

        elif self.cpu.running_process and next_process:
            #cpu voll, runq voll
            # strategy decission was to switch context

            # there is a another process, which should be run
            old_running_process = self.cpu.dispatch(next_process) # still in state L
            # decide what to do with the old process:
            if not old_running_process is None:
                self.addToMatchingQueue(old_running_process) # dispatch to the right queue
            next_run = True

        return next_run

    def schedule(self):

        #check the ea queues if there are finished processes. if so, append them to the queues
        finished_waiting_processes = self.__check_ea_queues()
        for p in finished_waiting_processes:
            self.addToMatchingQueue(p)


        #active = self.processManager.getActiveProcess()
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
                active = self.cpu.running_process # notwendig, da dispatch ausgefuehrt wurde
            if isinstance(next_section, Launch):
                # process will launch another process
                self.addToMatchingQueue(active)
                # @TODO: dispatch ist schedulingabhaengig! implementieren

        # collect information about resources
        sum_waiting_pcbs = sum(map(lambda x: len(x), self.ea_queues))  # Sum of all PCBs in EAQueues
        readyq_empty = True if len(self.ready_queue) == 0 else False  # ready queue empty?

        if not active and readyq_empty:
            # cpu leer, runq leer
            if sum_waiting_pcbs > 0:
                #but there are still waiting processes
                next_run = True
            else:
                next_run = False #and no more processes in ea_queue
        elif not active and not readyq_empty:
            # cpu leer, runq voll: dispatchen und nochmal laufen
            ready = self.ready_queue.pop()
            self.__refilQuantum(ready) # refill quantum for next process in cpu
            self.cpu.dispatch(ready)
            next_run = True
        elif active and not readyq_empty:
            # cpu voll, runq leer
            # there is no readyq_empty process...
            # reschedule: process in cpu belongs in cpu
            print 'reschedule process'
            self.__refilQuantum(self.cpu.running_process)
            next_run = True
        elif active and readyq_empty:
            next_run = self.howToSchedule.schedule(self)
        else:
            #unefined state
            raise RuntimeError("undefined scheduling state")

        self._loop_counter += 1 # count the scheduling-steps
        return next_run



    def __refilQuantum(self, pcb):
        """
        refill the pcb's time quantum
        :param pcb: pcb to refill
        """
        print "REFIL Quantum"

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
        print "add process to ready queue:",pcb
        # if rescheduled because of time quantum, add at the end, if it's because of preemption, add to the beginning
        self.howToSchedule.addToReadyQueue(scheduler=self, pcb=pcb)
        return True



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
                return Scheduler(strategy(timeslice, quantum))
        raise NotImplementedError("the requested scheduler [%s] could not be found. typo?" % strategy_str)