__author__ = 'Christoph Gerneth'

from manager import ProcessManager


class Section(object):
    pass


class TimeSection(Section):
    def __init__(self, duration):
        # time cannot be negative:
        if duration < 0:
            raise ValueError("Time cannot be negative!")
        self.__duration = duration
        self.__starting_at = None  # used to keep track of history events

    @property
    def starting_at(self):
        return self.__starting_at

    @starting_at.setter
    def starting_at(self, time):
        self.__starting_at = time

    @property
    def duration(self):
        return self.__duration

    @duration.setter
    def duration(self, time):
        self.__duration = time

    def __cmp__(self, other):
        return self.duration - other.duration


class ActionSection(Section):
    """Action Sections don't have a time, but can launch an action"""

    def __init__(self, action):
        self.duration = 0
        self.action = action


# concrete sections (Flyweight Pattern):

class Work(TimeSection):
    def __repr__(self):
        return "Work(%i)" % self.duration


class Wait(TimeSection):
    def __repr__(self):
        return "Wait(%i)" % self.duration


class Ready(TimeSection):
    def __repr__(self):
        return "Ready(%i)" % self.duration


class Launch(ActionSection):
    def __init__(self, action):
        # assert isinstance(action, PCB)
        super(Launch, self).__init__(action)

    def __repr__(self):
        return "Launch(%s)" % repr(self.action)


class Workplan(object):
    """
    the Workplan holds the Section in a chronological order.
    it is responsible for the right oder. A workplan can only begin with either a work or a launch section
    usage: wp = Workplan().work(10).wait(20).launch(process)
    """

    def __init__(self):
        self.plan = list()
        self.__pmanager = ProcessManager()

    # you can combine these functions in a row. they will get added to the plan
    def work(self, time):
        time = self.__combine(time, Work)
        self.plan.append(Work(time))
        return self

    def wait(self, time):
        time = self.__combine(time, Wait)
        if len(self.plan) == 0:
            raise TypeError("Workplan cannot begin with a waiting section")
        self.plan.append(Wait(time))
        return self

    def launch(self, process):
        """
        try to launch process
        :param process: PCB or process name as string
        :return: self
        """
        if isinstance(process, str):
            # lookup in taksmanager, if there is such a process and get pcb
            process = self.__pmanager.getProcessByName(process)
        self.plan.append(Launch(process))
        return self

    # to manipulate the internal data structure, use these functions:
    def pop(self, i=0):
        """
        get the first section from the workplan
        :param i: if you want another section from the worklan. (-1 for the last section)
        :return: first section by default or the section you define with parameter i
        :raise KeyError if empty
        """
        return self.plan.pop(0)

    def head(self):
        """
        get the first element
        :return: Section
        """
        return self.plan[0]

    def tail(self):
        """
        get the last element
        :return: Section
        """
        return self.plan[-1]

    def insert(self, element, i=0):
        """
        insert a Section in workplan
        :param element: Section
        :param i: Index
        """
        assert issubclass(element.__class__, (ActionSection, TimeSection))
        self.plan.insert(i, element)

    def __combine(self, time, type):
        """
        combine times if same type is same as ancestor: Work(10),Work(20) -> Work(30)
        :param time: time of section
        :param type: type of section
        :return: combined time if same type as ancestor, else original time
        """
        try:
            if isinstance(self.plan[-1], type):
                # if last section is the defined Type, combine both section times
                old_section = self.plan.pop()
                time = old_section.duration + time
        except IndexError:
            pass
        return time

    def __repr__(self):
        plan = map(lambda x: repr(x), self.plan)
        return "<Workplan: %s>" % "->".join(plan)
