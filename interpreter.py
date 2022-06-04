from boom_parser import Parser
from evaluator import NodeEvaluator


class Interpreter:
    def __init__(self):
        self.scope = dict({"global": {}})

    def loop(self):
        while True:
            source = input(": ")

            if source == "exit":
                return

            for i in Parser(source).parse():
                ev = NodeEvaluator(i, self.scope)
                ev.evaluate(i)
                self.scope = ev.scope
