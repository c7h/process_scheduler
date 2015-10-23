__author__ = 'Christoph Gerneth'


class Strategy(object):
    def __init__(self, *args, **kwargs):
        super(Strategy, self).__init__()

    def addToReadyQueue(self, scheduler, pcb):
        """
        add a process to the ready queue.
        if it's because of time quantum, add at the end, if it's because of preemption, add to the beginning
        :param queue: queue
        :param scheduler: access to the scheduler
        :return: queue
        """
        raise NotImplementedError("please implement meeeee")

    def schedule(self, scheduler):
        """
        MainLoop for Scheduling decision: should we dispatch the CPU or not?
        :return: next PCB from run queue or None if current running process can keep the cpu
        """
        raise NotImplementedError("please implement meeeeeeee :)")


class SimpleStrategy(Strategy):
    pass


class MultiLevelStrategy(Strategy):
    """
    MultiLevel Strategies use as simple-strategy for the queue-in-decision
    """
    def __init__(self):
        self.__secondaryStrategy = None

    @property
    def secondaryStrategy(self):
        if self.__secondaryStrategy is None:
            raise TypeError("Please set a Secondary strategy first")
        return self.__secondaryStrategy

    @secondaryStrategy.setter
    def secondaryStrategy(self, strategy):
        """
        set the secondary strategy. This strategy is always a SimpleStrategy like FiFo or RoundRobin
        :param strategy: SimpleStrategy
        """
        assert isinstance(strategy, SimpleStrategy)
        self.__secondaryStrategy = strategy