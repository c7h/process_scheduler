import unittest
from scenarios import FiFoScenario2

from process_scheduler.scheduler.core import SchedulerFactory
from process_scheduler.common.serializer import JsonSerializer

import json

class JSONSerializerTestCase(FiFoScenario2):
    def setUp(self):
        super(JSONSerializerTestCase, self).setUp()
        fifoscheduler = SchedulerFactory.getScheduler("FiFo")
        fifoscheduler.initialize("A")
        fifoscheduler.run()

    def test_generate_01(self):
        serializer = JsonSerializer()
        data = serializer.generateJson()
        print data
        try:
            json.loads(data)
        except ValueError:
            self.fail("json not valid")

    def test_generate_data(self):
        serializer = JsonSerializer()
        data = serializer.generateData()
        print data
        self.assertIsInstance(data, dict)

if __name__ == '__main__':
    unittest.main()
