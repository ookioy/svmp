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


class Lexeme:
    def __init__(self, line_num: int, token: TokenType, value: str, pos: int):
        self.line_num = line_num
        self.token = token
        self.value = value
        self.pos = pos


KNOWN_TAGS = {
    "<table>": TokenType.TAG_TABLE_OPEN,
    "</table>": TokenType.TAG_TABLE_CLOSE,
    "<tr>": TokenType.TAG_TR_OPEN,
    "</tr>": TokenType.TAG_TR_CLOSE,
    "<td>": TokenType.TAG_TD_OPEN,
    "</td>": TokenType.TAG_TD_CLOSE,
}


def lex_line(line_num: int, line_text: str) -> list[Lexeme]:
    tokens = []
    pos = 0
    length = len(line_text)

    while pos < length:
        if line_text[pos] in " \t\r\n":
            pos += 1
            continue

        ch = line_text[pos]

        if ch == "<":
            start = pos
            while pos < length and line_text[pos] != ">" and not line_text[pos].isspace():
                pos += 1
            if pos < length and line_text[pos] == ">":
                pos += 1
            tag_str = line_text[start:pos]
            token_type = KNOWN_TAGS.get(tag_str, TokenType.UNKNOWN)
            tokens.append(Lexeme(line_num, token_type, tag_str, start + 1))
            continue

        if ch in ("1", "2", "3"):
            tokens.append(Lexeme(line_num, TokenType.DIGIT, ch, pos + 1))
            pos += 1
            continue

        tokens.append(Lexeme(line_num, TokenType.UNKNOWN, ch, pos + 1))
        pos += 1

    tokens.append(Lexeme(line_num, TokenType.END, "END", length + 1))
    return tokens


class SyntaxErrorExceptions(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Lexeme]):
        self.tokens = tokens
        self.idx = 0

    def current(self) -> Lexeme:
        return self.tokens[self.idx]

    def match(self, expected_type: TokenType):
        curr = self.current()
        if curr.token == expected_type:
            self.idx += 1
            return curr
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувався тег '{expected_type.name}', але виявлено '{curr.value}'."
            )

    def parse_S(self):
        self.match(TokenType.TAG_TABLE_OPEN)
        self.parse_R()
        self.match(TokenType.TAG_TABLE_CLOSE)

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

    def parse_D(self):
        curr = self.current()
        if curr.token == TokenType.DIGIT:
            self.parse_B()
            self.parse_D_prime()
        elif curr.token == TokenType.TAG_TABLE_OPEN:
            self.parse_S()
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — очікувалася цифра (1, 2, 3) або '<table>', виявлено '{curr.value}'."
            )

    def parse_D_prime(self):
        curr = self.current()
        if curr.token == TokenType.DIGIT:
            self.parse_B()
            self.parse_D_prime()
        elif curr.token == TokenType.TAG_TD_CLOSE:
            return
        else:
            raise SyntaxErrorExceptions(
                f"Синтаксична — неочікуваний символ '{curr.value}'."
            )

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
            tokens = lex_line(i, line)

            lexical_error = None
            for tok in tokens:
                if tok.token == TokenType.UNKNOWN:
                    lexical_error = (
                        f"  [!] Помилка (символ {tok.pos}): Лексична — недопустима лексема '{tok.value}'.\n"
                        f"  ==> Висновок: НЕ НАЛЕЖИТЬ мові граматики.\n\n"
                    )
                    break

            if lexical_error:
                fout.write(lexical_error)
                continue

            parser = Parser(tokens)
            try:
                parser.parse()
                fout.write("  [+] Успіх: Синтаксичний аналіз пройдено.\n")
                fout.write("  ==> Висновок: НАЛЕЖИТЬ мові граматики.\n\n")
            except SyntaxErrorExceptions as e:
                curr_pos = parser.current().pos
                fout.write(f"  [!] Помилка (символ {curr_pos}): {e}\n")
                fout.write("  ==> Висновок: НЕ НАЛЕЖИТЬ мові граматики.\n\n")


if __name__ == "__main__":
    main()