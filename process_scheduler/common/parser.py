__author__ = 'Christoph Gerneth'
from plyplus import Grammar, STransformer

from process.process import Process, PCB
from process.workplan import Workplan

# The Grammar is defined here. The Syntax is EBNF-like
_syntaxParser = Grammar(r"""
start : scenario;

scenario : lane+ ;

lane : process '\:' phase;

phase : (work | launch) (',' (work | wait | launch))* ;

work : 'Work\(' length '\)' ;
wait : 'Wait\(' length '\)' ;
launch : 'Launch\(' letter '\)' ;


@process_name : letter ;
prio : '\d+' ;
process : process_name '\(' prio '\)' ;


length : '\d+' ;
letter : '[A-Z]' ;
NEWLINE : '[\n|]+' (%ignore) ;
SPACE : '[ ]+' (%ignore) ;
""")


class ProcessTransformer(STransformer):
    """
    The Process transformer takes a parsetree and visits every node. When it discovers a node called like a function,
    it executes the functions on it.
    """

    letter = lambda self, o: str(o.tail[0])
    prio =   lambda self, o: int(o.tail[0])
    length = lambda self, o: int(o.tail[0])

    def process(self, node):
        process_name = node.tail[0] # converted to str thanks to converter above :)
        process_prio = node.tail[1]
        pcb = PCB(Process(process_name),prio=process_prio)
        return pcb


class WorkplanTransformer(STransformer):
    letter = lambda self, o: str(o.tail[0])
    #prio =   lambda self, o: int(o.tail[0])
    length = lambda self, o: int(o.tail[0])

    def phase(self, node):
        w = Workplan()
        for i in node.tail:
            head = i.head
            value = i.tail[0]
            if head == 'work':
                w.work(int(value))
            elif head == 'wait':
                w.wait(int(value))
            elif head == 'launch':
                w.launch(str(value))
        print 'generated workplan', w
        return w


class LaneTransformer(STransformer):
    """
    Last transformer. responsible for linking PCB with Workplan
    """
    def lane(self, node):
        pcb = node.tail[0]
        workplan = node.tail[1]
        #combine them:
        pcb.process.workplan = workplan


def parseSyntax(processDescriptionSyntax):
    """
    method to parse process syntax and generate processes and PCBs.
    The workplan will be attached to the process structure.
    :param processDescriptionSyntax: Syntax in Process Description Language
    :return: nothing
    """
    assert isinstance(processDescriptionSyntax, str)
    tree =  _syntaxParser.parse(processDescriptionSyntax)
    process_transformer = ProcessTransformer()
    workplan_transformer = WorkplanTransformer()
    lane_transformer = LaneTransformer()

    process_ttree = process_transformer.transform(tree)
    workplan_ttree = workplan_transformer.transform(process_ttree)
    lane_transformer.transform(workplan_ttree)