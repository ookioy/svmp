from enum import Enum, auto

# S -> <table>R</table>
# R -> <tr>C</tr>R | e
# C -> <td>D</td>C | e
# D -> BD | B | S
# B -> 1 | 2 | 3


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


class SyntaxErrorExceptions(Exception):
    pass


class Parser:

    def __init__(self):
        self.curr_token = get_token()

    def current(self) -> Lex:
        if self.curr_token.token == TokenType.UNKNOWN:
            raise SyntaxErrorExceptions(
                f"Лексична — недопустима лексема '{self.curr_token.value}'."
            )
        return self.curr_token

    def match(self, expected_type: TokenType):
        curr = self.current()
        if curr.token == expected_type:
            # Зчитуємо наступну лексему з потоку
            self.curr_token = get_token()
            return curr
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувався тег '{expected_type.name}', але виявлено '{curr.value}'."
            )

    # S -> <table>R</table>
    def parse_S(self):
        self.match(TokenType.TAG_TABLE_OPEN)
        self.parse_R()
        self.match(TokenType.TAG_TABLE_CLOSE)

    # R -> <tr>C</tr>R | e
    def parse_R(self):
        curr = self.current()
        if curr.token == TokenType.TAG_TR_OPEN:
            self.match(TokenType.TAG_TR_OPEN)
            self.parse_C()
            self.match(TokenType.TAG_TR_CLOSE)
            self.parse_R()
        elif curr.token == TokenType.TAG_TABLE_CLOSE:
            return
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувалось '<tr>' або '</table>', але виявлено '{curr.value}'."
            )

    # C -> <td>D</td>C | e
    def parse_C(self):
        curr = self.current()
        if curr.token == TokenType.TAG_TD_OPEN:
            self.match(TokenType.TAG_TD_OPEN)
            self.parse_D()
            self.match(TokenType.TAG_TD_CLOSE)
            self.parse_C()
        elif curr.token == TokenType.TAG_TR_CLOSE:
            return
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувалось '<td>' або '</tr>', але виявлено '{curr.value}'."
            )

    # D -> BD | B | S
    def parse_D(self, allow_epsilon=False):
        curr = self.current()
        if curr.token == TokenType.DIGIT:
            self.parse_B()
            self.parse_D(allow_epsilon=True)
        elif curr.token == TokenType.TAG_TABLE_OPEN and not allow_epsilon:
            self.parse_S()
        elif allow_epsilon and curr.token == TokenType.TAG_TD_CLOSE:
            return
        else:
            if allow_epsilon:
                raise SyntaxErrorExceptions(
                    f"Синтаксична — неочікуваний символ '{curr.value}'."
                )
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувалася цифра (1, 2, 3) або '<table>', виявлено '{curr.value}'."
            )

    # B -> 1 | 2 | 3
    def parse_B(self):
        curr = self.current()
        if curr.token == TokenType.DIGIT and curr.value in ("1", "2", "3"):
            self.match(TokenType.DIGIT)
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувалася цифра 1, 2 або 3, виявлено '{curr.value}'."
            )

    def parse(self):
        self.parse_S()
        if self.current().token != TokenType.END:
            curr = self.current()
            raise SyntaxErrorExceptions(
                f"Синтаксична — зайві символи після таблиці: '{curr.value}'."
            )


def main():
    with open("input.txt", "r", encoding="utf-8") as fin:
        lines = [line.strip() for line in fin if line.strip()]

    with open("output.txt", "w", encoding="utf-8") as fout:
        for i, line in enumerate(lines, start=1):
            fout.write(f"Речення №{i}: {line}\n")

            init_line(i, line)

            parser = Parser()

            try:
                parser.parse()
                fout.write("  [+] Успіх: Синтаксичний аналіз пройдено.\n")
                fout.write("  ==> Висновок: НАЛЕЖИТЬ мові граматики.\n\n")
            except SyntaxErrorExceptions as e:
                fout.write(f"  [!] Помилка: {e}\n")
                fout.write("  ==> Висновок: НЕ НАЛЕЖИТЬ мові граматики.\n\n")


if __name__ == "__main__":
    main()