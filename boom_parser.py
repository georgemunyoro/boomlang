import enum
from os import uname
from typing import Any, List
from lexer import BASE_TOKEN_IDS, Lexer, Token


class Node:
    value: Any

    def __init__(self, value, name):
        self.value = value
        self.name = name

    def __str__(self) -> str:
        return f"({self.name}: {self.value})"


class UnaryNode(Node):
    ...


class BinaryNode(Node):
    def __init__(self, left, right, value):
        self.value = value
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left.value}{self.value}{self.right.value})"


class Parser:
    tokens: List[Token]

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.lexer = Lexer(source)
        self.tokens = self.lexer.lex()
        self.running = False

    def parse(self) -> List[Node]:
        for i, token in enumerate(self.tokens):
            if token.value in BASE_TOKEN_IDS.keys():
                self.tokens[i] = Token(
                    BASE_TOKEN_IDS[token.value], token.value
                )

        self.running = True
        while self.running:
            yield (self.parse_expr())

    @property
    def curr_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        self.running = False
        return Token("END", "END")

    @property
    def prev_token(self) -> Token:
        if self.pos >= 0:
            return self.tokens[self.pos - 1]
        self.running = False
        return Token("END", "END")

    @property
    def next_token(self) -> Token:
        if self.pos < len(self.tokens) - 1:
            return self.tokens[self.pos + 1]
        self.running = False
        return Token("END", "END")

    def parse_func_args(self):
        args = []
        while self.curr_token.id != "CLOS_PAREN":
            args.append(self.parse_expr())
            if self.curr_token.id == "SYMB_COMMA":
                self.pos += 1
                continue
            else:
                break
        return UnaryNode(args, "PARAM_LIST")

    def parse_expr(self):
        if self.curr_token.id == "ITEM":
            if self.next_token.id == "OPEN_PAREN":
                n = BinaryNode(
                    UnaryNode(self.curr_token.value, "ITEM"),
                    Node("", ""),
                    "FUNC",
                )
                self.pos += 2
                n.right = self.parse_func_args()
                if self.curr_token.id == "CLOS_PAREN":
                    self.pos += 1
                    return n
                else:
                    if self.curr_token.id == "END":
                        return n
                    else:
                        raise Exception(
                            f"Expected ')', found {self.curr_token.value} instead"
                        )
            elif self.next_token.id.startswith("OPER_"):
                n = BinaryNode(
                    UnaryNode(self.curr_token.value, "ITEM"),
                    Node("", ""),
                    self.next_token.id,
                )
                self.pos += 2
                n.right = self.parse_expr()
                return n
            else:
                self.pos += 1
                return UnaryNode(self.prev_token.value, "ITEM")

        elif (
            self.curr_token.id == "OPEN_PAREN"
            or self.curr_token.id == "OPEN_BRACE"
        ):
            self.pos += 1
            expr = self.parse_expr()
            self.pos += 1
            return expr

        elif (
            self.curr_token.id == "NUMBER_LIT"
            or self.curr_token.id == "STRING_LIT"
        ):
            if self.next_token.id.startswith("OPER_"):
                n = BinaryNode(
                    UnaryNode(self.curr_token.value, self.curr_token.id),
                    UnaryNode("", ""),
                    self.next_token.id,
                )
                self.pos += 2
                n.right = self.parse_expr()
                return n
            else:
                self.pos += 1
                return UnaryNode(self.prev_token.value, self.prev_token.id)

        self.running = False
