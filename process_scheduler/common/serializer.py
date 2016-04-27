from process_scheduler.process.manager import ProcessManager
from process_scheduler.process.workplan import Wait, Work, Ready, Launch
from evaluator import StrategyEvaluator, ProcessEvaluator

from uuid import uuid1
import json


class JsonSerializer(object):
    def __init__(self):
        self.se = StrategyEvaluator()
        self.pe = ProcessEvaluator()
        self.pm = ProcessManager()

    def getIDforLane(self, pcb):
        """
        get the lane id for a pcb
        :param pcb: PCB
        :return: int: index of the lane
        """
        process = self.pm.getProcessByName(pcb.process.name)
        return self.pm.jobs.index(process)


    def __generateItems(self):
        items = list()
        for p in self.pm.jobs:
            sections_list = self.pe.getHistorySectionByType(p, Ready)
            sections_list.extend(self.pe.getHistorySectionByType(p, Work))
            sections_list.extend(self.pe.getHistorySectionByType(p, Wait))

            for section in sections_list:

                if isinstance(section, Wait):
                    state = "paused"
                elif isinstance(section, Work):
                    state = "running"
                elif isinstance(section, Ready):
                    state = "ready"

                job_dict = {"lane": self.getIDforLane(p),
                            "id": uuid1().get_urn(),
                            "start": section.starting_at,
                            "end": section.starting_at + section.duration,
                            "state": state,
                            "details": section.__repr__(),
                            }

                items.append(job_dict)
        return items

    def __generateLaunches(self):
        launches = list()
        for p in self.pm.jobs:
            launch_list = self.pe.getHistorySectionByType(p, Launch)
            for launch in launch_list:
                launch_event = {"trigger": self.getIDforLane(p),
                                "target": self.getIDforLane(launch.action),
                                "timestamp": launch.starting_at,
                                }
                launches.append(launch_event)
        return launches

    def __generateStrategyEvaluation(self):
        evaluation = dict()
        evaluation["cpu utilization"] = self.se.getAverageCPUusage()
        evaluation["mean response time"] = self.se.getMeanResponseTime()
        return evaluation

    def __combineResult(self):
        period = self.se.getPeriodDuration()
        launches = self.__generateLaunches()
        items = self.__generateItems()
        lanes = [pe.process.name for pe in self.pm.jobs]

        strategy_eval = self.__generateStrategyEvaluation()

        quantum_data = list()

        data = {'time_begin': 0,
                'time_end': period,
                'lanes': lanes,
                'items': items,
                'quantum_data': quantum_data,
                'launches': launches,
                'strategy evaluation': strategy_eval,
                }

        return data

    def generateJson(self):
        """
        return a json in a defined format
        :return: JSON-string
        """
        data = self.__combineResult()
        return json.dumps(data, indent=4, sort_keys=True)

    def generateData(self):
        """
        return a dictionary of python-object in a defined format
        :return: dict
        """
        data = self.__combineResult()
        return data
