from typing import List


BASE_TOKEN_IDS = {
    ",": "SYMB_COMMA",
    "(": "OPEN_PAREN",
    ")": "CLOS_PAREN",
    "{": "OPEN_PAREN",
    "}": "CLOS_PAREN",
    ";": "CLOS_EXPRN",
    "=": "OPER_EQUAL",
    "+": "OPER_ADDTN",
    "-": "OPER_MINUS",
    "*": "OPER_MULTI",
    "%": "OPER_MODUL",
    "/": "OPER_FSLSH",
    "\\": "SYMB_BSLSH",
    "==": "OPER_IS_EQUAL",
    "!=": "OPER_IS_NEQUAL",
    ">=": "OPER_IS_MORE_EQUAL",
    "<=": "OPER_IS_LESS_EQUAL",
    ">": "OPER_IS_MORE",
    "<": "OPER_IS_LESS",
    "||": "OPER_OR",
    "&&": "OPER_AND",
}


class Token:
    def __init__(self, id: str, value) -> None:
        self.id = id
        self.value = value

    def __str__(self) -> str:
        return f"<{self.id}>{self.value}</{self.id}>"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.in_string = False
        self.in_string_type = None
        self.in_number = False
        self.tokens = []
        self.buffer = ""

    def strip_comments(self):
        self.source = "\n".join(
            [
                line
                for line in self.source.split("\n")
                if not line.strip().startswith("#")
            ]
        )

    def lex(self) -> List[str]:
        self.strip_comments()

        DOUBLE_QUOTE = '"'
        SINGLE_QUOTE = "'"

        self.strip_comments()

        for i in self.source:
            self.buffer += i
            if self.in_string:
                self.handle_string_char(i)
                continue

            if self.in_number:
                if self.handle_digit_char(i) is False:
                    continue

            if i.isdigit():
                self.in_number = True
                self.buffer = i
                continue

            if i == DOUBLE_QUOTE or i == SINGLE_QUOTE:
                self.buffer = ""
                self.in_string = True
                self.in_string_type = i
                continue

            if i == " " or i == "\n":
                self.tokens.append(Token("ITEM", self.buffer[:-1]))
                self.buffer = ""
                continue

            if (
                i in "|=&"
                and (self.tokens[::-1][0].value + i) in BASE_TOKEN_IDS.keys()
            ):
                t_val = self.tokens[::-1][0].value + i
                self.tokens[len(self.tokens) - 1] = Token(
                    BASE_TOKEN_IDS[t_val], t_val
                )
                self.buffer = ""
                continue

            if i in BASE_TOKEN_IDS.keys():
                if self.buffer[:-1].strip() != "":
                    self.tokens.append(Token("ITEM", self.buffer[:-1].strip()))
                self.tokens.append(Token(BASE_TOKEN_IDS[i], i))
                self.buffer = ""
                continue

        if self.in_number:
            self.handle_digit_char("", include_last_char=True)

        if self.in_string:
            self.handle_string_char("", include_last_char=True)

        return [
            token
            for token in self.tokens
            if token.value != "" and token.value != "\n"
        ]

    def handle_digit_char(self, i: str, include_last_char: bool = False):
        """
        Handle digit characters if currently dealing with a number.

        Adds the number currently stored in the buffer to the token list,
        clears the buffer, and returns True if the number has actually
        ended. In which case the lexer will continue on to find out what
        else the current character is.

        Does nothing and returns false if the character was in fact a number.
        """
        if not i.isdigit() and i != ".":
            self.in_number = False
            self.tokens.append(
                Token(
                    "NUMBER_LIT",
                    self.buffer if include_last_char else self.buffer[:-1],
                )
            )
            self.buffer = ""
            return True
        return False

    def handle_string_char(self, i: str, include_last_char: bool = False):
        """
        Handle string literal characters if currently dealing with a string.

        Adds the string currently stored in the buffer to the token list,
        clears the buffer, and returns True if the character was of the same
        type used to open and string has actually ended.

        Does nothing and returns False if the character was in fact
        still part of a string.
        """
        if i == self.in_string_type:
            self.in_string = False
            self.tokens.append(
                Token(
                    "STRING_LIT",
                    self.buffer if include_last_char else self.buffer[:-1],
                )
            )
            self.buffer = ""
            return True
        return False
