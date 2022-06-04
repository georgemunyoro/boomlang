from ast import arg
from copy import copy
from ctypes import Union
from tkinter import E, W
from turtle import right
from typing import Dict
from uuid import uuid4

from boom_parser import BinaryNode, Parser, UnaryNode


class NodeEvaluator:
    def __init__(self, node: str, scope: Dict):
        self.node = node
        self.scope = {
            "global": {
                "append": self.append,
                "join": self.join,
                "pop": self.pop,
                "index": self.index,
                "set_index": self.set_index,
                "del": self.delete,
                "len": self.len,
                "str": self.str,
                "in": self.input,
                "int": self.int_decl,
                "out": self.out,
                "list": self.decl_list,
                "false": False,
                "true": True,
                "mod": self.mod,
                "floor": self.floor,
                **scope["global"],
            },
        }

        self.scope_stack = ["global"]

    @staticmethod
    def delete(self, arr, index):
        if isinstance(arr, dict):
            del arr[str(index)]
            return arr
        else:
            return [i for i, j in enumerate(arr) if j != int(index)]

    @staticmethod
    def set_index(self, arr, index, value):
        if isinstance(arr, dict):
            arr[str(index)] = value
            return arr
        else:
            arr[int(index)] = value
            return arr

    @staticmethod
    def str(self, *args):
        return str(*args)

    @staticmethod
    def index(self, arr, index):
        if isinstance(arr, dict):
            return arr[str(index)]
        else:
            return arr[int(index)]

    @staticmethod
    def join(self, arr, *args):
        return "".join([arr, *args])

    @staticmethod
    def append(self, arr, *args):
        if isinstance(arr, str):
            return "".join([arr, *args])
        elif arr is None:
            return list(args)
        else:
            return arr + list(args)

    @staticmethod
    def len(self, arr):
        return len(arr)

    @staticmethod
    def pop(self, arr):
        return arr.pop()

    @staticmethod
    def out(self, *args):
        return print(*args)

    @staticmethod
    def input(self, *args):
        return input(*args)

    @staticmethod
    def int_decl(self, *args):
        return int(*args)

    @staticmethod
    def decl_list(self, *args):
        return list(args)

    @staticmethod
    def mod(self, x, y):
        return x % y

    @staticmethod
    def floor(self, x, y):
        return x // y

    def evaluate(self, node):
        if isinstance(node, UnaryNode):
            return self.evaluate_unary_node(node)
        return self.evaluate_binary_node(node)

    def evaluate_unary_node(self, node: UnaryNode):
        if node.name == "STRING_LIT":
            return node.value

        elif node.name == "NUMBER_LIT":
            return float(node.value)

        elif node.name == "ITEM":
            for i in range(len(self.scope_stack)):
                depth = len(self.scope_stack) - i
                scope_key = "".join(self.scope_stack[:depth]).strip()
                scope_exists = scope_key in self.scope.keys()
                if (
                    scope_exists
                    and node.value.split(".")[0]
                    in self.scope[scope_key].keys()
                ):
                    if "." in node.value:
                        val = self.scope[scope_key][node.value.split(".")[0]]
                        for index, j in enumerate(node.value.split(".")):
                            if index > 0:
                                val = val[j]
                        return val
                    return self.scope[scope_key][node.value]

    def evaluate_binary_node(self, node: BinaryNode):
        if node is None:
            return

        if node.value == "FUNC":
            return self.evaluate_function_node(node)

        elif node.value == "OPER_ADDTN":
            return self.evaluate(node.left) + self.evaluate(node.right)
        elif node.value == "OPER_MULTI":
            return self.evaluate(node.left) * self.evaluate(node.right)
        elif node.value == "OPER_MINUS":
            return self.evaluate(node.left) - self.evaluate(node.right)
        elif node.value == "OPER_FSLSH":
            return self.evaluate(node.left) / self.evaluate(node.right)
        elif node.value == "OPER_MODUL":
            return self.evaluate(node.left) % self.evaluate(node.right)

        # Assignment operator
        elif node.value == "OPER_EQUAL":
            scope_key = "".join(self.scope_stack).strip()
            if scope_key not in self.scope.keys():
                self.scope[scope_key] = dict({})
            self.scope[scope_key][node.left.value] = self.evaluate(node.right)

        elif node.value == "OPER_IS_EQUAL":
            return self.evaluate(node.left) == self.evaluate(node.right)
        elif node.value == "OPER_IS_NEQUAL":
            return self.evaluate(node.left) != self.evaluate(node.right)

        elif node.value == "OPER_IS_MORE":
            return self.evaluate(node.left) > self.evaluate(node.right)
        elif node.value == "OPER_IS_LESS":
            return self.evaluate(node.left) < self.evaluate(node.right)
        elif node.value == "OPER_IS_MORE_EQUAL":
            return self.evaluate(node.left) >= self.evaluate(node.right)
        elif node.value == "OPER_IS_LESS_EQUAL":
            return self.evaluate(node.left) <= self.evaluate(node.right)

        elif node.value == "OPER_OR":
            return self.evaluate(node.left) or self.evaluate(node.right)
        elif node.value == "OPER_AND":
            return self.evaluate(node.left) and self.evaluate(node.right)

    def evaluate_function_node(self, node: BinaryNode):
        if node.left.value == "return":
            params = [self.evaluate(p) for p in node.right.value]
            return params[0]

        elif node.left.value == "map":
            return self.evaluate_map_node(node)

        elif node.left.value == "include":
            return self.evaluate_include_node(node)

        elif node.left.value == "for":
            return self.evaluate_for_loop_node(node)

        elif node.left.value == "func":
            return self.evaluate_block_node(node)

        elif node.left.value == "if":
            return self.evaluate_conditional_node(node)

        else:
            return self.evaluate_function_call(node)

    def evaluate_map_node(self, node: BinaryNode):
        temp_dict = dict()
        for i in node.right.value:
            temp_dict[str(i.left.value).strip()] = self.evaluate(i.right)
        return temp_dict

    def evaluate_include_node(self, node: BinaryNode):
        with open(node.right.value[0].value, "r") as f:
            source = f.read()
            gs = dict({"global": {}})
            for i in Parser(source).parse():
                ev = NodeEvaluator(i, gs)
                ev.evaluate(i)
                gs = ev.scope
            self.scope = {**self.scope, **gs}

    def evaluate_for_loop_node(self, node: BinaryNode):
        self.evaluate(node.right.value[0])
        while self.evaluate(node.right.value[1]):
            self.evaluate(node.right.value[3])(self)
            self.evaluate(node.right.value[2])

    def evaluate_conditional_node(self, node: BinaryNode):
        if self.evaluate(node.right.value[0]):
            return self.evaluate(node.right.value[1])(self)
        else:
            return self.evaluate(node.right.value[2])(self)

    def evaluate_block_node(self, node: BinaryNode):
        def evaluation(self, *args):
            for i in node.right.value:
                curr_eval = self.evaluate(i)
                if curr_eval is not None:
                    return curr_eval

        return evaluation

    def evaluate_function_call(self, node: BinaryNode):
        FUNC_RUN_ID = str(uuid4())

        self.scope_stack.append(FUNC_RUN_ID)
        scope_key = "".join(self.scope_stack).strip()
        if scope_key not in self.scope.keys():
            self.scope[scope_key] = dict({})

        named_args = dict({})
        for i in node.right.value:
            if i.value == "OPER_EQUAL":
                named_args[i.left.value] = self.evaluate(i.right)
        if len(named_args.keys()) > 0:
            self.scope[scope_key]["args"] = named_args

        params = [
            self.evaluate(p)
            for p in node.right.value
            if p is not None and p.value != "OPER_EQUAL"
        ]
        res = self.evaluate(node.left)(self, *params)
        self.scope_stack.pop()
        return res
