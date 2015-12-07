from process.manager import ProcessManager
from process.workplan import Work, Wait, Ready


class BaseEvaluator(object):
    def __init__(self):
        self.manager = ProcessManager()


class ProcessEvaluator(BaseEvaluator):
    """
    the ProcessEvaluator calculates values for a specific process.
    :return: tuple(from, to)
    """

    def getAverageWaitingTime(self, pcb_or_str):
        raise NotImplementedError

    def getWaitTime(self, pcb_or_str):
        """Summe aller Zeitraeume, in denen Prozess auf irgend etwas wartet.
        Bei uns: Zeit in Zustaenden W und B"""
        pcb = self.__arg_to_pcb(pcb_or_str)
        waiting_sections = self.getHistorySectionByType(pcb, Wait)
        ready_sections = self.getHistorySectionByType(pcb, Ready)
        waiting_sections.extend(ready_sections)
        waiting_times = sum(map(lambda x: x.duration, waiting_sections))
        return waiting_times


    def getServiceTime(self, pcb_or_str):
        """Summe aller Zeitraume, in denen Prozess die CPU belegt Bei uns: Zeit in Zustand L"""
        pcb = self.__arg_to_pcb(pcb_or_str)
        busy_sections = self.getHistorySectionByType(pcb, Work)
        service_time = sum(map(lambda x: x.duration, busy_sections))
        return service_time


    def getPeriodForPCB(self, pcb_or_str):
        pcb = self.__arg_to_pcb(pcb_or_str)

        try:
            last = pcb.process.history.tail()
            first = pcb.process.history.head()
        except IndexError:
            # history is empyt
            pass
        else:
            first_occured_at = first.starting_at
            terminating_at = last.starting_at + last.duration
            return (first_occured_at, terminating_at)

    def __arg_to_pcb(self, pcb_or_str):
        """the promisse to return a pcb object...."""
        if isinstance(pcb_or_str, str):
            pcb = self.manager.getProcessByName(pcb_or_str)
        else:
            pcb = pcb_or_str
        return pcb

    def _getReadySectionsForPCB(self, pcb_or_str):
        """
        some ready sections are not part of the history yet or are too short.
        This function fills this holes
        :param pcb_or_str: Name of the PCB or PCB-Object itself
        :return: list of ready sections
        """
        pcb = self.__arg_to_pcb(pcb_or_str)
        ready_secs = list()
        for i in range(len(pcb.process.history.plan)):
            cur = pcb.process.history.plan[i]
            try:
                ne = pcb.process.history.plan[i+1]
            except IndexError:
                # no more next object
                break
            if isinstance(cur, Ready):
                cur.ending_at = ne.starting_at
                cur.duration = cur.ending_at - cur.starting_at # udpdate duration
                ready_secs.append(cur)
        return ready_secs



    def getHistorySectionByType(self, pcb, SectionType):
        if isinstance(SectionType, Ready):
            # generate the ready sections on demand
            section_times = self._getReadySectionsForPCB(pcb)
        else:
            section_times = filter(lambda x: isinstance(x, SectionType), pcb.process.history.plan)
        section_times.sort(key=lambda x: x.ending_at)
        return section_times


class StrategyEvaluator(BaseEvaluator):
    def getAverageCPUusage(self):
        """
        the average CPU usage is a value from 0-100.
        remeber! period duration / busy time (time where cpu was not idle)
        :return: float
        """


        idle_time = 0
        busy_sections = list()
        for p in self.manager.jobs:
            # collect all waiting sections
            p_waitings = filter(lambda x: isinstance(x, Work), p.process.history.plan)
            busy_sections.extend(p_waitings)

        # sort busy_sections by ending_at
        busy_sections.sort(key=lambda x: x.ending_at)

        # merge work sections. explanation: image a the scheduling diagram. If one process is launched after another,
        # the launchtime is 0. The CPU is never empyt at this point; there is always a running process.
        # ergo: the transition point is 0
        while len(busy_sections) >= 2:
            c = busy_sections.pop(0)
            n = busy_sections[0]
            transition_point = (n.ending_at - n.duration) - c.ending_at
            if transition_point == 0:
                # sections are continuously
                pass
            elif transition_point > 0:
                # we have a wait!
                idle_time += transition_point
            else:
                # two process are overlapping. snap! this should never happen.
                raise RuntimeError("Two processes are overlaping")

        period_duration = self.getPeriodDuration()
        busy_time = period_duration - idle_time

        cpu_utilization = float(busy_time)/float(period_duration)
        return cpu_utilization





    def getPeriodDuration(self):
        """
        how long did the Schedule took?
        :return: int
        """
        # find the process with the latest endpoint in history
        pe = ProcessEvaluator()
        last_sections = list()
        for p in self.manager.jobs:
            period = pe.getPeriodForPCB(p)
            last_sections.append(period[1])
        return max(last_sections)