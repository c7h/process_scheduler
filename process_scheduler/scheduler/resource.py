__author__ = 'Christoph Gerneth'
from timer import SystemTimer, TimerListener
from process.process import PCB
from process.workplan import Wait, Launch
from common.types import ProcessTerminatedMessage


class Resource(object):
    """
    a Resource. Nothing to see here....
    """

    def __init__(self):
        self._queue = list()

    @property
    def queue(self):
        return self._queue

    def __len__(self):
        return len(self._queue)


class EAQueue(Resource, TimerListener):
    def __init__(self):
        super(EAQueue, self).__init__()
        SystemTimer().register(self)
        self.ready_processes = list()

    def notify(self, time):
        self.work(time)

    def work(self, time):
        """
        decrease waiting process times and check, if there is a ready process
        """
        for p in self._queue:
            try:
                what_was_done = p.process.doWork(time)
                print "###> EAQueue decreased wait of process", p, ":", what_was_done
            except ProcessTerminatedMessage as e:
                # Process terminated...
                p.setInactive()
                what_was_done = e.last_section
                print e.message
            try:
                future_section = p.process.workplan.head()  # look in the future
                SystemTimer().next_tick_in(future_section.duration)  # tell the timer when the next interrupt will occur
            except IndexError:
                # this one was the last section
                pass  # we don't have to inform the timer, because there will be no more sections
            else:
                # if future_section is not a Wait-section,
                if not isinstance(future_section, Wait):
                    # we are done with waiting!
                    # process can switch to ready queue if he wants to launch again...
                    self._queue.remove(p)
                    self.ready_processes.append(p)

    def append(self, pcb):
        """always appends process at the end of the list"""
        # TODO: if we want to do EA-Scheduling as well, we need a strategy depended insert
        pcb.setWaiting()
        self._queue.append(pcb)
        print "##> %s appended to E/A Queue: %s" % (pcb, self._queue)

    @property
    def processes(self):
        return self._queue

    def pickup_ready_processes(self):
        """
        pickup ready processes from the ready list
        :return ready pcbs
        """
        pickup_list = list(self.ready_processes)  # make a copy of the list
        self.ready_processes = list()  # and cleanup ready_list
        return pickup_list

    def __getitem__(self, key):
        return self._queue[key]

    def __iter__(self):
        """
        add ability to iterate though the queue.
        """
        # todo: we could inherit the 'Resource'-superclass from list
        return iter(self._queue)

    def __repr__(self):
        return "<EAQueue(%i) %s>" % (len(self._queue), self._queue)


class CPU(Resource, TimerListener):
    """
    this is a CPU resource with a single Core
    We use this resource for logging purposes and a one-place waiting queue.
    """

    def __init__(self):
        super(CPU, self).__init__()
        self._queue = [None]  # there is only place for one active process in the CPU.
        self.dispatch_counter = 0  # count the number of dispatches

        # register at the timer-listener:
        SystemTimer().register(self)

        self.__last_dispatch = 0

    def notify(self, time):
        """is executed on every timer-tick of the SystemTimer. Let time go by"""
        self.work(time)
        # try:
        #     self.work(time)
        # except ProcessTerminatedMessage as e:
        #     self._queue[0] = None # process is done

    def work(self, time):
        """
        :param time: time to work without break
        :return: true if process is done after worktime, false if there is a section left
        """
        print "---> [%i] CPU work section entered at %i" % (time, SystemTimer().timecounter)

        running_pcb = self.running_process

        try:
            what_was_done = running_pcb.process.doWork(time)
            print "[%i] CPU just did %s for %ims on process %s" \
                  % (time, what_was_done, what_was_done.duration, running_pcb)
        except AttributeError:
            # no process in CPU
            print '[%i] CPU empty' % time
        except ProcessTerminatedMessage as e:
            # process terminated after execution
            print "[%i] Process terminated after execution: %s" % (time, e.message)
        else:
            if isinstance(what_was_done, Launch):
                # cpu executed launch section
                # launches are now executed in add-to-matching queue method in the core scheduler
                pass
                # @TODO: finish this shit

        try:
            future_section = running_pcb.process.workplan.head()
        except IndexError:
            # no more future section in workplan left. process is done.
            self.__terminateProcess(running_pcb)
        except AttributeError:
            # running pcb is empyt
            pass  # nothing to update
        else:
            SystemTimer().next_tick_in(future_section.duration)

        # trying to decrease quantum
        if SystemTimer().timehammer and time > 0 and running_pcb != None:
            try:
                running_pcb.decrease_quantum()
            except ValueError as e:
                print "CPU notification: ", e

        print "<--- [%i] CPU work section left at %i" % (time, SystemTimer().timecounter)

    @property
    def time_since_dispatch(self):
        return SystemTimer().timecounter - self.__last_dispatch

    @property
    def running_process(self):
        """
        :return: the running process. if there is no running process, None is returned.
        """
        return self._queue[0]

    def __terminateProcess(self, pcb):
        assert isinstance(pcb, PCB)
        print "Process", pcb, "terminated..."
        pcb.setInactive()
        self._queue[0] = None

    def dispatch(self, pcb=None):
        """
        dispatch means we switch processes on the CPU. If a process enters the CPU, it's state gets set to Laufend
        :param pcb: feed the processor with a pcb (in reality, this is not pcb of course). If the pcb  is None,
        the old process was the last process and the processor stops working.
        :return: old pcb
        """
        old_process = self._queue.pop()
        # the old process is still in state running. there are tree possible transitions:
        # waiting, ready or inactive

        # @TODO: decide if we maintain process state here or at the scheduler.

        self._queue.append(pcb)
        self.dispatch_counter += 1  # count the context switches... because we can
        self.__last_dispatch = SystemTimer().timecounter
        if isinstance(pcb, PCB):
            pcb.setRunning()  # set process state to L
        return old_process
