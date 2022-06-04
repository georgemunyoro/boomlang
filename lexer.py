from typing import List


BASE_TOKEN_IDS = {
    ",": "SYMB_COMMA",
    "(": "OPEN_PAREN",
    ")": "CLOS_PAREN",
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


def lex(code: str) -> List[str]:
    DOUBLE_QUOTE = '"'
    SINGLE_QUOTE = "'"

    in_string = False
    in_string_type = None

    in_number = False
    tokens = []

    buffer = ""

    for i in code:
        buffer += i
        if in_string:
            if i == in_string_type:
                in_string = False
                tokens.append(Token("STRING_LIT", buffer[:-1]))
                buffer = ""
            continue

        if in_number:
            if not i.isdigit() and i != ".":
                in_number = False
                tokens.append(Token("NUMBER_LIT", buffer[:-1]))
                buffer = ""
            else:
                continue

        if i.isdigit():
            in_number = True
            buffer = i
            continue

        if i == DOUBLE_QUOTE or i == SINGLE_QUOTE:
            buffer = ""
            in_string = True
            in_string_type = i
            continue

        if i == " " or i == "\n":
            tokens.append(Token("ITEM", buffer[:-1]))
            buffer = ""
            continue

        if i in "|=&" and (tokens[::-1][0].value + i) in BASE_TOKEN_IDS.keys():
            t_val = tokens[::-1][0].value + i
            tokens[len(tokens) - 1] = Token(BASE_TOKEN_IDS[t_val], t_val)
            buffer = ""
            continue

        if i in BASE_TOKEN_IDS.keys():
            if buffer[:-1].strip() != "":
                tokens.append(Token("ITEM", buffer[:-1].strip()))
            tokens.append(Token(BASE_TOKEN_IDS[i], i))
            buffer = ""
            continue

    return [
        token for token in tokens if token.value != "" and token.value != "\n"
    ]
