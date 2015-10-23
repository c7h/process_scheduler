__author__ = 'c7h'

import unittest
from process.workplan import Workplan
from process.workplan import Wait, Work

from process.process import PCB, Process


class TestWorkplan(unittest.TestCase):
    def test_createWorkplan_01(self):
        wp = Workplan().work(10).wait(5).work(30)
        print wp
        self.assertIsInstance(wp, Workplan)

    def test_createWorkplan_02(self):
        # wait cannot be the first section of the workplan.
        self.assertRaises(TypeError, Workplan.wait, 10)

    def test_createWorkplan_03(self):
        #now we test the launch sections



        p1 = PCB(Process('A'))
        p2 = PCB(Process('B'))

        wp1 = Workplan().launch('B').work(10)
        wp2 = Workplan().work(30)

        p1.process.workplan = wp1
        p2.process.workplan = wp2

        #processManager.getProcess('B').workplan = wp1

    def test_combineSections_01(self):
        expected = [Work(30), Wait(10)]
        wp = Workplan().work(10).work(10).work(10).wait(10)
        self.assertListEqual(expected, wp.plan, 'something went wrong while combining')

    def test_cannot_wait_first(self):
        wp = Workplan()
        self.assertRaises(TypeError, wp.wait, 10)

    def test_not_negative(self):
        #negative values are not allowed and will raise a ValueError
        self.assertRaises(ValueError, Workplan().work, -10)

    def test_pop_01(self):
        #get the next section from the workplan.
        wp = Workplan().work(10).wait(20).work(30)
        # get first section
        section = wp.pop()
        self.assertEqual(Work(10), section)

    def test_pop_02(self):
        #test pop from empty workplan
        wp = Workplan().work(10)
        wp.pop()
        #worplan now empty
        self.assertRaises(IndexError, wp.pop)


if __name__ == '__main__':
    unittest.main()
