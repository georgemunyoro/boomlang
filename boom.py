import sys
from evaluator import NodeEvaluator
from boom_parser import BinaryNode, Parser, UnaryNode
import math
from pprint import pprint


with open(sys.argv[1], "r") as f:
    source = f.read()
    gs = dict({"global": {}})

    for i in Parser(source).parse():
        ev = NodeEvaluator(i, gs)
        ev.evaluate(i)
        gs = ev.scope
