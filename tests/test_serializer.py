import unittest
from scenarios import FiFoScenario2
from scheduler.core import SchedulerFactory
from common.serializer import JsonSerializer

class JSONSerializerTestCase(FiFoScenario2):
    def setUp(self):
        super(JSONSerializerTestCase, self).setUp()
        fifoscheduler = SchedulerFactory.getScheduler("FiFo")
        fifoscheduler.initialize("A")
        fifoscheduler.run()

    def test_generate_01(self):
        serializer = JsonSerializer()
        print serializer.generateJson()

if __name__ == '__main__':
    unittest.main()
