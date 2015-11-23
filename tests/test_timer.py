__author__ = 'Christoph Gerneth'

import unittest
from scheduler.timer import TimerListener, SystemTimer


class Foobar(TimerListener):
    """
    This example shows how the TimerListener is working. Don't forget to register yourself at the SystemTimer!
    """

    def __init__(self):
        st = SystemTimer()
        st.register(self)  # register

    def notify(self, timestamp):
        print '[%s] timestamp received form sender: %i' % (id(self), timestamp)


class TimerCase(unittest.TestCase):
    def setUp(self):
        self.stimer = SystemTimer()
        self.stimer.timecounter = 0
        self.stimer.timeunit = 10

    def test_createTimer(self):
        self.assertIsInstance(self.stimer, SystemTimer)

    # @unittest.skip('weird problem with the singleton...')
    def test_timerTick_01(self):
        # weird... it seems that unittest is not invalidating old TimerInstances.
        for i in range(5):
            self.stimer.tick()
        self.assertEqual(self.stimer.timecounter, 50)

    def test_register_listener_01(self):
        res1, res2 = Foobar(), Foobar()
        stimer = SystemTimer()
        stimer.tick()

    def test_singletonType_01(self):
        t1 = SystemTimer()
        t2 = SystemTimer()
        self.assertIs(t1, t2)

    def test_singletonType_02(self):
        t1 = SystemTimer()
        t2 = SystemTimer()
        print "SystemTimer Object is", id(t1)
        self.assertEqual(id(t1), id(t2))

    def test_setAbsoluteTime(self):
        timeunit = self.stimer.timeunit
        self.stimer.tick()
        self.stimer.setAbsoluteTime(timeunit * 2)
        self.assertEqual(self.stimer.timecounter, timeunit * 2)

    def test_next_tick_in(self):
        timeunit = self.stimer.timeunit  # usually, the next step is in 10 ms
        self.stimer.next_tick_in(3)  # but now, the next step is in 3ms
        self.stimer.tick()  # do a tick
        self.assertEqual(self.stimer.timecounter, 3)

    def tearDown(self):
        # because the timer class is implemented as Singleton, we have weird side effects
        # while unittesting. So we need un-register every listener after a run.
        self.stimer.unregisterAll()
        # ...hmm.. just to make sure, drop the SystemTimer instance
        SystemTimer._drop()


if __name__ == '__main__':
    unittest.main()
