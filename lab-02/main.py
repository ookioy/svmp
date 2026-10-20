from enum import Enum, auto


class TokenType(Enum):
    TAG_TABLE_OPEN = auto()
    TAG_TABLE_CLOSE = auto()
    TAG_TR_OPEN = auto()
    TAG_TR_CLOSE = auto()
    TAG_TD_OPEN = auto()
    TAG_TD_CLOSE = auto()
    DIGIT = auto()
    END = auto()
    UNKNOWN = auto()


class Lex:

    def __init__(self, line_num: int, token: TokenType, value: str):
        self.line_num = line_num
        self.token = token
        self.value = value

    def __str__(self):
        return f"<{self.line_num}, {self.token.name}, {self.value}>"


current_line = ""
current_line_num = 0
pos = 0

KNOWN_TAGS = {
    "<table>": TokenType.TAG_TABLE_OPEN,
    "</table>": TokenType.TAG_TABLE_CLOSE,
    "<tr>": TokenType.TAG_TR_OPEN,
    "</tr>": TokenType.TAG_TR_CLOSE,
    "<td>": TokenType.TAG_TD_OPEN,
    "</td>": TokenType.TAG_TD_CLOSE,
}


def init_line(line_num: int, line_text: str):
    global current_line, current_line_num, pos
    current_line = line_text
    current_line_num = line_num
    pos = 0


def get_token() -> Lex:
    global pos, current_line, current_line_num

    while pos < len(current_line) and current_line[pos] in " \t\r\n":
        pos += 1

    if pos >= len(current_line):
        return Lex(current_line_num, TokenType.END, "END")

    ch = current_line[pos]

    if ch == "<":
        start = pos
        while (
            pos < len(current_line)
            and current_line[pos] != ">"
            and not current_line[pos].isspace()
        ):
            pos += 1
        if pos < len(current_line) and current_line[pos] == ">":
            pos += 1
        tag = current_line[start:pos]
        token_type = KNOWN_TAGS.get(tag, TokenType.UNKNOWN)
        return Lex(current_line_num, token_type, tag)

    if ch in ("1", "2", "3"):
        pos += 1
        return Lex(current_line_num, TokenType.DIGIT, ch)

    pos += 1
    return Lex(current_line_num, TokenType.UNKNOWN, ch)


def main():
    with open("input.txt", "r", encoding="utf-8") as fin:
        lines = fin.readlines()

    with open("tokens.txt", "w", encoding="utf-8") as fout:
        for i, line in enumerate(lines, start=1):
            init_line(i, line)
            while True:
                tok = get_token()

                if tok.token == TokenType.UNKNOWN:
                    print(
                        f"Рядок {i}: зустріли невідому лексему '{tok.value}', завершення програми."
                    )
                    exit()
                if tok.token == TokenType.END:
                    break

                fout.write(f"{tok}\n")


if __name__ == "__main__":
    main()