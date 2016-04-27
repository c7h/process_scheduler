__author__ = 'Christoph Gerneth'

import unittest
from process_scheduler.common.types import SingletonType

class SingletonObject(object):
    __metaclass__ = SingletonType



class SingletonTypeTestCase(unittest.TestCase):
    def test_singleton_01(self):
        fancy_singleton_instance = SingletonObject()
        the_same_singelton = SingletonObject()
        self.assertEqual(id(fancy_singleton_instance), id(the_same_singelton))

    def test_drop_singleton(self):
        s1 = SingletonObject()
        print "Singleton id before drop:", id(s1)
        SingletonObject._drop()
        s2 = SingletonObject()
        print "Singleton id after drop and re-creation:", id(s2)
        self.assertNotEqual(id(s1), id(s2))

if __name__ == '__main__':
    unittest.main()
