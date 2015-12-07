__author__ = 'Christoph Gerneth'
from random import choice
from uuid import uuid1
from warnings import warn
from copy import copy, deepcopy

from state import State

from workplan import Workplan
from manager import ProcessManager
from scheduler.timer import SystemTimer

from common.types import ProcessTerminatedMessage


class Process(object):
    def __init__(self, name=None):
        """
        :param name: Names are like PIDs in real life. They must be a unique string in our system.
        They are converted to an uppercase representation, so, names are NOT case sensitive!
        """
        self.name = self._unique_name() if name is None else name
        self.name = self.name.upper()  # convert names to uppercase!
        self.__workplan = None  # the workplan stores every event in the future
        self.__history = Workplan()  # we store the history here...

    @property
    def history(self):
        """
        :returns: Events in the past
        :return: Workplan
        """
        return self.__history

    @property
    def workplan(self):
        """
        get the current workplan
        :return: Workplan. Empty if not initialized
        """
        if self.__workplan is None:
            return Workplan()
        return self.__workplan

    @workplan.setter
    def workplan(self, workplan):
        self.__workplan = workplan

    def doWork(self, time=None):
        """
        tell process to do some work from the workplan
        :param time: how long should the process work?
        If no time is provided, work one TimeSection (plus Action Section)
        :return Section: finished section
        :Raise ProcessTerminatedMessage if process is done!
        """

        try:
            active_section = self.__workplan.pop()  # get section from workplan
        except IndexError:
            # there is no more section in workplan. Process Terminated.
            # we use a clever messaging system to inform the Scheduler as soon as a process terminated.
            raise ProcessTerminatedMessage("Workplan empty - Process terminated!", last_section=self.__history.head())

        new_history_section = deepcopy(active_section)  # create a copy of the section


        if time is None:
            time = active_section.duration # work till the end of the active section (typically for FiFo)

        worked_time = min(active_section.duration, time)  # calculate time you can spend in section

        # maintain history and workplan
        if active_section.duration - worked_time > 0:
            # add updated section at the first place of the workplan (if time left)
            active_section.duration -= worked_time
            self.workplan.insert(active_section)  # don't touch active_section from now an...

        new_history_section.duration = worked_time  # time spent working...
        new_history_section.ending_at = SystemTimer().timecounter # injecting a new attribute
        new_history_section.starting_at = SystemTimer().timecounter - worked_time
        self.history.insert(new_history_section, i=len(self.history.plan))  # insert element at the end of the history

        # - decide if we should update system timer here or at the scheduler after call (work).
        # I think we should update system timer here: It's not sure that the work-function is working for the whole time
        # it the workplan says, we work only 10ms, but the scheduler granted a timeslice for 20, we will return after 10
        # to avoid double checks, update system timer here.
        # .......
        # okay, the Scheduler Should be responsible for the ticks
        # SystemTimer().setRelativeTime(worked_time)  # A NEW STEP WAS DONE! NOTIFY EVERYONE!!!!

        # if time left, work again!
        if worked_time < time:
            self.doWork(time - worked_time)
        return new_history_section




    def _unique_name(self):
        """
        helper function to generate a unique name
        """
        return uuid1().urn

    def _random_name(self):
        """
        generate a random name - this is not necessary, but fancy!
        attention! no guarantee to be unique.
        """
        warn(DeprecationWarning)
        randname = []
        charset = ["A", "B", "C", "D", "E", "F"]
        for i in range(4):
            randname.append(choice(charset))
        return "".join(randname)

    def __repr__(self):
        return "<Process %s>" % self.name


class PCB(object):
    def __init__(self, process, prio=0, state=State.I, quantum=4, timeslice=10, deadline=10):
        assert isinstance(prio, int)
        self.state = state  # initial state is inactive
        self.process = process  # a process can't exist without a pcb in our system (composite)
        self.priority = prio

        self.__quantum = quantum
        self.__timeslice = timeslice
        self.__remaining_time = 0
        self.__deadline = deadline

        ProcessManager().addPCB(self)  # register at the Manager, please

    def refill_time_quantum(self):
        raise NotImplementedError("implement me")

    def getTimeLeftInCurrentSection(self):

        self.process
        # raise NotImplementedError("todo: implement me")


    # state setter... there are some boundaries due to the rules of our state-machine.
    # The following transition are allowed (besides calling the same state again - these calls have no effect)
    # I -> B
    # L -> I
    # L -> W
    # L -> B
    # B -> L
    # W -> B
    def setRunning(self):
        if self.state is State.B or self.state is State.L:
            self.state = State.L
        else:
            raise RuntimeError("forbidden transition between process states: %s -> %s"
                               % (self.state, State.L))

    def setWaiting(self):
        if self.state is State.L or self.state is State.W:
            self.state = State.W
        else:
            raise RuntimeError("forbidden transition between process states: %s -> %s"
                               % (self.state, State.W))

    def setInactive(self):
        if self.state is State.L or self.state is State.I:
            self.state = State.I
        else:
            raise RuntimeError("wrong transition between process states: %s -> %s"
                               % (self.state, State.I))

    def setReady(self):
        if self.state in (State.I, State.L, State.W, State.B):
            self.state = State.B
        else:
            raise RuntimeError("wrong transition between process states: %s -> %s"
                               % (self.state, State.B))

    def __repr__(self):
        return "<PCB for %s>" % self.process.name