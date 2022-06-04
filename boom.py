import sys
from evaluator import NodeEvaluator
from boom_parser import BinaryNode, Parser, UnaryNode
from interpreter import Interpreter


def run_file(filepath: str):
    with open(filepath, "r") as f:
        source = f.read()
        gs = dict({"global": {}})

        for i in Parser(source).parse():
            ev = NodeEvaluator(i, gs)
            ev.evaluate(i)
            gs = ev.scope


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        terp = Interpreter()
        terp.loop()
