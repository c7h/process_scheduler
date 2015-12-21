from process.manager import ProcessManager
from process.workplan import Wait, Work, Ready, Launch
from evaluator import StrategyEvaluator, ProcessEvaluator
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
                            "id": "%s (id:%i)" % (section.__repr__(), id(section)),
                            "start": section.starting_at,
                            "end": section.starting_at + section.duration,
                            "state": state,
                            "details": "implement me"
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

    def generateJson(self):
        period = self.se.getPeriodDuration()
        launches = self.__generateLaunches()
        items = self.__generateItems()
        lanes = [pe.process.name for pe in self.pm.jobs]

        quantum_data = list()

        data = {'time_begin': 0,
                'time_end': period,
                'lanes': lanes,
                'items': items,
                'quantum_data': quantum_data,
                'launches': launches,
                }

        return json.dumps(data, indent=4, sort_keys=True)
