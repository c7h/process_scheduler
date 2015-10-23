__author__ = 'c7h'

from strategy import MultiLevelStrategy
from simple import FiFo, RoundRobin


class MLsecondFiFo(MultiLevelStrategy):
    def __init__(self):
        self.secondaryStrategy = FiFo()

    def schedule(self):
        return True


class MLsecondRR(MultiLevelStrategy):
    def __init__(self, timeslice, quantum):
        self.secondaryStrategy = RoundRobin(timeslice, quantum)

    def schedule(self):
        return True
