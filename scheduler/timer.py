__author__ = 'Christoph Gerneth'

from common.types import SingletonType

class TimerListener(object):

    def notify(self, timestamp):
        """
        you get notified every tick
        :param timestamp: is last tick duration by design.
        """
        raise NotImplementedError("please implement me!! you get called by this function if you implement me!")

class SystemTimer(object):
    __metaclass__ = SingletonType

    def __init__(self, timeunit=10):
        """
        The system timer keeps track of the time.
        :param timeunit: how long is the duration between every tick
        :return:
        """
        self.timecounter = 0
        self.timeunit = timeunit
        self.next_temp_timeunit = timeunit # initial to timeunit
        self.last_tick_duration = 0

        self.__listeners = []

    #items can register at the SystemTimer to get notified (Observer Pattern)

    def register(self, listener):
        #everyone who is interested in the SystemTime should register here...
        self.__listeners.append(listener)

    def unregister(self, listener):
        self.__listeners.remove(listener)

    def unregisterAll(self):
        self.__listeners = []

    def setAbsoluteTime(self, time):
        """
        manipulate the time of the TimeCounter.
        :param time: int - must be higher than current time,
        because you cannot go back in time ;-)
        :raise Value Error if you try to set time to the past
        """
        if time >= self.timecounter:
            self.timecounter = time
        else:
            raise ValueError("Time was %ims but unfortunately you cannot time travel [%ims]"
                             % (int(self.timecounter), int(time))
            )

    def setRelativeTime(self, time):
        """
        add time to the time counter
        :param time:
        :return:
        """
        self.timecounter += time
        self.last_tick_duration = time
        #self.__notify_all() #and notify all listeners that an event occurred

    def next_tick_in(self, time):
        """
        if there will be an event closer than `timeunit`ms, we have to trigger the scheduler at this event.
        example: timeunit is 10ms and we have a process like A:Work(10),Wait(5),Work(10)
        after the first step, we will have a `next_tick_in` 5ms. The Timer will trigger the next scheduler event in 5ms
        instead of 10ms
        """
        if time < self.timeunit and time < self.next_temp_timeunit:
            self.next_temp_timeunit = time

    def tick(self):
        """
        make a system tick. this is used for preemptive scheduling strategies.
        all listeners will be notified.
        """
        step = self.__getStepWidth()
        self.__resetStepWidth()

        self.timecounter += step
        self.last_tick_duration = step
        self.__notify_all()

    def __getStepWidth(self):
        return min(self.next_temp_timeunit, self.timeunit)

    def __resetStepWidth(self):
        """next step width will be the default again"""
        self.next_temp_timeunit = self.timeunit

    def __notify_all(self):
        for l in self.__listeners:
            l.notify(self.last_tick_duration)