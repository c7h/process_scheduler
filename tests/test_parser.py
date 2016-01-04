__author__ = 'c7h'

import unittest
from common.parser import ProcessTransformer, WorkplanTransformer, _syntaxParser, parseSyntax, Workplan
from process.workplan import ProcessManager


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        # prepare ProcessManager....
        ProcessManager().jobs = []

        self.example_string = """
X(0):Work(90)
A(9):Work(20),Launch(B),Wait(10),Work(20)
B(7):Work(13),Wait(37),Work(10)
"""

        self.oneliner_string = """X(0):Work(90) A(9):Work(20),Launch(B),Wait(10),Work(20) B(7):Work(13),Wait(37),Work(10)"""

    def test_parse_grammar_01(self):
        tree = _syntaxParser.parse(self.example_string)
        print tree.pretty()

    def test_transformer(self):
        tree = _syntaxParser.parse(self.example_string)
        proc_transformer = ProcessTransformer()
        wplan_transformer = WorkplanTransformer()

        # it's important to use the ProcessTransformer first
        obj_tree = proc_transformer.transform(tree)
        # processes are now created, launch sections need existing processes
        wplan_transformer.transform(obj_tree)

        # check if the rigt process was created
        pm = ProcessManager()
        pcb_b = pm.getProcessByName('B')

        # we check the priorith and the name here....
        self.assertTrue(pcb_b.process.name, 'B')
        self.assertTrue(pcb_b.priority, 7)

    def test_parseSyntaxMethod(self):
        # execute syntaxparser
        parseSyntax(self.example_string)
        jobs = ProcessManager().jobs
        print 'JOOOBS', jobs
        self.assertTrue(len(jobs) == 3)

    def test_parseSyntaxMethod_02(self):
        parseSyntax(self.example_string)
        pcb_x = ProcessManager().getProcessByName('X')
        workplan = pcb_x.process.workplan
        plan_soll = Workplan().work(90)
        self.assertListEqual(plan_soll.plan,
                             workplan.plan)

    def test_parseOneliner(self):
        parseSyntax(self.oneliner_string)
        pcb_x = ProcessManager().getProcessByName("X")
        plan_soll = Workplan().work(90)
        plan_ist = pcb_x.process.workplan
        self.assertListEqual(plan_soll.plan, plan_ist.plan)

    def tearDown(self):
        ProcessManager._drop()


if __name__ == '__main__':
    unittest.main()
