# coding=utf-8
__author__ = 'Christoph Gerneth'


from scheduler.core import SchedulerFactory
from process.manager import ProcessManager

from parser import parseSyntax #we use the parser to create processes

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
    print welcome

    while True:
        # read-eval-print-loop
        syntax = read_loop() #read
        try:
            parseSyntax(syntax) # eval
        except Exception as e:
            print 'Something went wrong:', e.message
            print 'try it again!' #print
        else:
            print 'sucessfully read syntax' #print
            print syntax.strip()
            break
    # prozesse sind erzeugt - process manager ist initialisiert. weiter im text....
    init_process = raw_input("Welcher Prozess soll zuerst laufen? [%s]:"
                             % " oder ".join([p.process.name for p in  ProcessManager().jobs]))
    # welcher scheduler soll verwendet werden?
    while True:
        requested_scheduler = raw_input("Welchen Scheduler soll ich verwenden? ")
        q = input("initial process quantum: ")
        ts = input("initial process timeslice: ")
        try:
            scheduler = SchedulerFactory.getScheduler(requested_scheduler,timeslice=ts, quantum=q)
        except Exception as e:
            print 'something went wrong:', e
            print 'try one of these:', SchedulerFactory.getPossibleChoices()
        else:
            scheduler.initialize(init_process)
            scheduler.run()
            break

def read_loop():
    in_text = ""
    while True:
        #read-loop
        read_text = raw_input("please give me your process syntax: ")
        if read_text == "":
            break
        else:
            in_text += "\n" + read_text
    return in_text


if __name__ == '__main__':
    main()