# coding=utf-8
__author__ = 'Christoph Gerneth'

from process_scheduler.scheduler.core import SchedulerFactory
from process_scheduler.process.manager import ProcessManager

from parser import parseSyntax  # we use the parser to create processes
from evaluator import StrategyEvaluator, ProcessEvaluator

welcome = u"""
███████╗ ██████╗██╗  ██╗███████╗██████╗ ██╗   ██╗██╗     ██╗███╗   ██╗ ██████╗
██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗██║   ██║██║     ██║████╗  ██║██╔════╝
███████╗██║     ███████║█████╗  ██║  ██║██║   ██║██║     ██║██╔██╗ ██║██║  ███╗
╚════██║██║     ██╔══██║██╔══╝  ██║  ██║██║   ██║██║     ██║██║╚██╗██║██║   ██║
███████║╚██████╗██║  ██║███████╗██████╔╝╚██████╔╝███████╗██║██║ ╚████║╚██████╔╝
╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝
██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗███████╗██████╗
██║   ██║██║██╔════╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔════╝██╔══██╗
██║   ██║██║███████╗██║   ██║███████║██║     ██║  ███╔╝ █████╗  ██████╔╝
╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══╝  ██╔══██╗
 ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗██║███████╗███████╗██║  ██║
  ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
"""


def main():
    """
    REPL-environment CLI-Client
    :return:
    """

    print welcome

    while True:
        # read-eval-print-loop
        syntax = read_loop()  # read
        try:
            parseSyntax(syntax)  # eval
        except Exception as e:
            print 'Something went wrong:', e.message
            print 'try it again!'  # print
        else:
            print 'sucessfully read syntax'  # print
            print syntax.strip()
            break
    # prozesse sind erzeugt - process manager ist initialisiert. weiter im text....
    init_process = raw_input("Welcher Prozess soll zuerst laufen? [%s]:"
                             % " oder ".join([p.process.name for p in ProcessManager().jobs]))
    # welcher scheduler soll verwendet werden?
    while True:
        requested_scheduler = raw_input("Welchen Scheduler soll ich verwenden? ")
        q = input("initial process quantum: ")
        ts = input("initial process timeslice: ")
        try:
            scheduler = SchedulerFactory.getScheduler(requested_scheduler, timeslice=ts, quantum=q)
        except Exception as e:
            print 'something went wrong:', e
            print 'try one of these:', SchedulerFactory.getPossibleChoices()
        else:
            scheduler.initialize(init_process)
            scheduler.run()
            print_scheduler_results()
            print_process_results()
            break


def print_scheduler_results():
    evaluator = StrategyEvaluator()
    print "Scheduling results for the Scheduler:"
    print "mean response time:", evaluator.getMeanResponseTime()
    print "CPU usage: %.f" % (evaluator.getAverageCPUusage() * 100)
    print "overall duration:", evaluator.getPeriodDuration()


def print_process_results():
    e = ProcessEvaluator()
    processes = ProcessManager().jobs
    print "Results for single processes:"
    for p in processes:
        values = {"p_name": p.process.name,
                  "turnaround": e.getTurnaroundTime(p),
                  "response": sum(e.getResponseTime(p)),
                  "wait": e.getWaitTime(p),
                  "service": e.getServiceTime(p)
                  }

        print "Process %(p_name)3s: turnaround time %(turnaround).2f | avg. response time %(response).2f | wait time %(wait).2f | service time %(service).2f" % values


def read_loop():
    in_text = ""
    while True:
        # read-loop
        read_text = raw_input("please give me your process syntax: ")
        if read_text == "":
            break
        else:
            in_text += "\n" + read_text
    return in_text


if __name__ == '__main__':
    main()
