from enum import Enum
import re

class TokenType(Enum):
    
    DEF      = "def"
    CLASS    = "class"
    IF       = "if"
    ELIF     = "elif"
    ELSE     = "else"
    FOR      = "for"
    WHILE    = "while"
    IN       = "in"
    RETURN   = "return"
    PRINT    = "print"
    TRUE     = "True"
    FALSE    = "False"
    NONE     = "None"
    AND      = "and"
    OR       = "or"
    NOT      = "not"
    IS       = "is"
    TRY      = "try"
    EXCEPT   = "except"
    FINALLY  = "finally"
    RAISE    = "raise"
    AS       = "as"
    IMPORT   = "import"
    FROM     = "from"
    PASS     = "pass"
    BREAK    = "break"
    CONTINUE = "continue"
    GLOBAL   = "global"
    NONLOCAL = "nonlocal"
    LAMBDA   = "lambda"
    DEL      = "del"
    ASSERT   = "assert"
    WITH     = "with"
    YIELD    = "yield"

    
    IDENTIFIER = "IDENTIFIER"
    NUMBER     = "NUMBER"
    STRING     = "STRING"
    FSTRING    = "FSTRING"

    
    PLUS         = "+"
    MINUS        = "-"
    MULTIPLY     = "*"
    DIVIDE       = "/"
    FLOOR_DIVIDE = "//"
    MODULO       = "%"
    POWER        = "**"


    PLUS_EQUALS         = "+="
    MINUS_EQUALS        = "-="
    MULTIPLY_EQUALS     = "*="
    DIVIDE_EQUALS       = "/="
    FLOOR_DIVIDE_EQUALS = "//="
    MODULO_EQUALS       = "%="
    POWER_EQUALS        = "**="

    
    BITWISE_AND = "&"
    BITWISE_OR  = "|"
    BITWISE_XOR = "^"
    TILDE       = "~"
    LSHIFT      = "<<"
    RSHIFT      = ">>"

   
    EQUALS        = "="
    DOUBLE_EQUALS = "=="
    NOT_EQUALS    = "!="
    LESS_THAN     = "<"
    GREATER_THAN  = ">"
    LESS_EQUAL    = "<="
    GREATER_EQUAL = ">="

   
    LPAREN    = "("
    RPAREN    = ")"
    LBRACKET  = "["
    RBRACKET  = "]"
    LBRACE    = "{"
    RBRACE    = "}"
    COMMA     = ","
    COLON     = ":"
    SEMICOLON = ";"
    DOT       = "."
    AT        = "@"
    ARROW     = "->"

    
    NEWLINE = "NEWLINE"
    INDENT  = "INDENT"
    DEDENT  = "DEDENT"
    COMMENT = "COMMENT"
    EOF     = "EOF"


class Token:
    def __init__(self, token_type, value, line, column):
        self.type   = token_type
        self.value  = value
        self.line   = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class LexerError(Exception):
    def __init__(self, message, line, column, suggestion=None):
        self.message    = message
        self.line       = line
        self.column     = column
        self.suggestion = suggestion
        super().__init__(message)


class Lexer:
    def __init__(self, code):
        self.code         = code
        self.tokens       = []
        self.indent_stack = [0]
        self._bracket_depth = 0       
        self.keywords     = {
            "def", "class", "if", "elif", "else",
            "for", "while", "in", "return", "print",
            "True", "False", "None", "and", "or", "not", "is",
            "try", "except", "finally", "raise", "as",
            "import", "from", "pass", "break", "continue",
            "global", "nonlocal", "lambda", "del", "assert",
            "with", "yield",
        }

   

    def tokenize(self):
        self.code = self.code.replace("\r\n", "\n").replace("\r", "\n")
        lines     = self.code.split("\n")

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            self.invalid_char(line, line_num)
            self.mixed_indent(line, line_num)

            if self._bracket_depth == 0:
                indent_level = len(line) - len(line.lstrip())
                self.handleindentation(indent_level, line_num)

            stripped = line.strip()
            if stripped.startswith("#"):
                self.tokens.append(Token(TokenType.COMMENT, stripped, line_num, 1))
                continue

            self.tokenizeline(stripped, line_num, len(line) - len(line.lstrip()))

            if self._bracket_depth == 0:
                self.tokens.append(Token(TokenType.NEWLINE, "\\n", line_num, len(line)))

        final_line = len(lines)
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "", final_line, 0))

        self.tokens.append(Token(TokenType.EOF, "", final_line, 0))
        return self.tokens

    

    def invalid_char(self, line, line_num):
        if "\t" in line:
            pos = line.index("\t") + 1
            raise LexerError("Tab character found", line_num, pos,
                              "Use spaces instead of tabs")

    def mixed_indent(self, line, line_num):
        indent = line[:len(line) - len(line.lstrip())]
        if "\t" in indent and " " in indent:
            raise LexerError("Mixed tabs and spaces", line_num, 1,
                              "Use only spaces for indentation")

    def handleindentation(self, indent_level, line_num):
        current = self.indent_stack[-1]
        if indent_level > current:
            self.indent_stack.append(indent_level)
            self.tokens.append(Token(TokenType.INDENT, "", line_num, 1))
        elif indent_level < current:
            while self.indent_stack and indent_level < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(TokenType.DEDENT, "", line_num, 1))

    

    def tokenizeline(self, line, line_num, base_column):
        i = 0
        while i < len(line):
            char  = line[i]
            column = base_column + i + 1

            
            if char.isspace():
                i += 1
                continue

           
            if char == "#":
                break

            
            _rest = line[i:]
            _is_valid_num_prefix = bool(
                re.match(r'^0[xXbBoO]', _rest) or          
                re.match(r'^\d+[eE][+\-]?\d', _rest) or   
                re.match(r'^\d*\.\d+[eE]', _rest)          
            )
            if not _is_valid_num_prefix:
                _bad_id = re.match(r'\d+[a-zA-Z_]+', _rest)
                if _bad_id:
                    raise LexerError(f"Invalid identifier '{_bad_id.group(0)}'",
                                      line_num, column,
                                      "Identifiers cannot start with a digit")

            if char.isdigit() or (char == '.' and i + 1 < len(line) and line[i+1].isdigit()):
                num, length = self.parsenumber(line, i, line_num, column)
                self.tokens.append(Token(TokenType.NUMBER, num, line_num, column))
                i += length
                continue

           
            if char in ("'", '"'):
                string, length = self.parsestring(line, i, line_num)
                self.tokens.append(Token(TokenType.STRING, string, line_num, column))
                i += length
                continue

            
            if char in ('f', 'F', 'r', 'b') and i + 1 < len(line) and line[i+1] in ('"', "'"):
                if char in ('f', 'F'):
                    fstr, length = self.parsefstring(line, i, line_num)
                    self.tokens.append(Token(TokenType.FSTRING, fstr, line_num, column))
                    i += length
                    continue
               
                _, skip = self.parsestring(line, i + 1, line_num)
                raw_val = line[i + 2: i + 1 + skip - 1]
                self.tokens.append(Token(TokenType.STRING, raw_val, line_num, column))
                i += 1 + skip
                continue

           
            if char.isalpha() or char == "_":
                identifier, length = self.parseidentifier(line, i)
                ttype = TokenType(identifier) if identifier in self.keywords else TokenType.IDENTIFIER
                self.tokens.append(Token(ttype, identifier, line_num, column))
                i += length
                continue

            
            three = line[i:i+3]
            three_ops = {
                "//=": TokenType.FLOOR_DIVIDE_EQUALS,
                "**=": TokenType.POWER_EQUALS,
            }
            if three in three_ops:
                self.tokens.append(Token(three_ops[three], three, line_num, column))
                i += 3
                continue

           
            two = line[i:i+2] if i + 1 < len(line) else ""
            two_ops = {
                "//": TokenType.FLOOR_DIVIDE,
                "**": TokenType.POWER,
                "==": TokenType.DOUBLE_EQUALS,
                "!=": TokenType.NOT_EQUALS,
                "<=": TokenType.LESS_EQUAL,
                ">=": TokenType.GREATER_EQUAL,
                "+=": TokenType.PLUS_EQUALS,
                "-=": TokenType.MINUS_EQUALS,
                "*=": TokenType.MULTIPLY_EQUALS,
                "/=": TokenType.DIVIDE_EQUALS,
                "%=": TokenType.MODULO_EQUALS,
                "->": TokenType.ARROW,
                "<<": TokenType.LSHIFT,
                ">>": TokenType.RSHIFT,
            }
            if two in two_ops:
                self.tokens.append(Token(two_ops[two], two, line_num, column))
                i += 2
                continue

            single = {
                "+": TokenType.PLUS,   "-": TokenType.MINUS,
                "*": TokenType.MULTIPLY, "/": TokenType.DIVIDE,
                "%": TokenType.MODULO,  "=": TokenType.EQUALS,
                "<": TokenType.LESS_THAN, ">": TokenType.GREATER_THAN,
                "(": TokenType.LPAREN,  ")": TokenType.RPAREN,
                "[": TokenType.LBRACKET, "]": TokenType.RBRACKET,
                "{": TokenType.LBRACE,  "}": TokenType.RBRACE,
                ",": TokenType.COMMA,   ":": TokenType.COLON,
                ";": TokenType.SEMICOLON, ".": TokenType.DOT,
                "@": TokenType.AT,      "~": TokenType.TILDE,
                "&": TokenType.BITWISE_AND, "|": TokenType.BITWISE_OR,
                "^": TokenType.BITWISE_XOR,
            }
            if char in single:
                ttype = single[char]
                self.tokens.append(Token(ttype, char, line_num, column))
                # Track bracket depth
                if char in ('(', '[', '{'):
                    self._bracket_depth += 1
                elif char in (')', ']', '}'):
                    self._bracket_depth = max(0, self._bracket_depth - 1)
                i += 1
                continue

            raise LexerError(f"Unrecognized character '{char}'",
                             line_num, column)

    

    def parsenumber(self, line, start, line_num, column):
        i = start
        
        if (line[i] == '0' and i + 1 < len(line) and
                line[i + 1] in ('x', 'X', 'o', 'O', 'b', 'B')):
            i += 2   
            while i < len(line) and line[i] in '0123456789abcdefABCDEF_':
                i += 1
            return line[start:i], i - start
        
        dot_count = 0
        while i < len(line) and (line[i].isdigit() or line[i] == '.'):
            if line[i] == '.':
                dot_count += 1
                if dot_count > 1:
                    raise LexerError("Invalid number format", line_num, column,
                                     "A number can contain only one decimal point")
            i += 1
        
        if i < len(line) and line[i] in ('e', 'E'):
            i += 1
            if i < len(line) and line[i] in ('+', '-'):
                i += 1
            while i < len(line) and line[i].isdigit():
                i += 1
        return line[start:i], i - start

    def parsestring(self, line, start, line_num):
        if start >= len(line):
            raise LexerError("Invalid string", line_num, start + 1)

        quote = line[start]

        if start + 2 < len(line) and line[start:start+3] == quote * 3:
            i = start + 3
            buf = ""

            while i < len(line):
                if i + 2 < len(line) and line[i:i+3] == quote * 3:
                    value = bytes(buf, "utf-8").decode("unicode_escape")
                    return value, i - start + 3

                buf += line[i]
                i += 1

            raise LexerError("Unclosed triple-quoted string", line_num, start + 1)

        i = start + 1
        buf = ""

        while i < len(line):
            if line[i] == "\\":
                if i + 1 < len(line):
                    buf += line[i]
                    buf += line[i + 1]
                    i += 2
                else:
                    buf += "\\"
                    i += 1
                continue

            if line[i] == quote:
                value = bytes(buf, "utf-8").decode("unicode_escape")
                return value, i - start + 1

            buf += line[i]
            i += 1

        raise LexerError("Unclosed string", line_num, start + 1)

    def parsefstring(self, line, start, line_num):
        """Parse f"..." — returns raw content (without quotes), length consumed."""
        i = start + 1          
        quote = line[i]
        
        if line[i:i+3] in ('"""', "'''"):
            close = line[i:i+3]
            i    += 3
            buf   = ""
            while i < len(line):
                if line[i:i+3] == close:
                    return buf, (i + 3) - start
                buf += line[i]
                i   += 1
            raise LexerError("Unclosed f-string", line_num, start + 1)
       
        i  += 1
        buf = ""
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line):
                buf += line[i:i+2]
                i   += 2
                continue
            if line[i] == quote:
                return buf, (i + 1) - start
            buf += line[i]
            i   += 1
        raise LexerError("Unclosed f-string", line_num, start + 1)

    def parseidentifier(self, line, start):
        i = start
        while i < len(line) and (line[i].isalnum() or line[i] == "_"):
            i += 1
        return line[start:i], i - start



if __name__ == "__main__":
    print("Enter Python code (press Enter twice to finish):\n")
    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append(line)
        else:
            empty_count = 0
            lines.append(line)
    source = "\n".join(lines).rstrip()
    try:
        tokens = Lexer(source).tokenize()
        print(f"\n{'TYPE':<25} VALUE")
        print("-" * 40)
        for t in tokens:
            print(f"{t.type.name:<25} {t.value!r}")
    except LexerError as e:
        print(f"\nLexer Error  line {e.line}, col {e.column}: {e.message}")
        if e.suggestion:
            print("Suggestion:", e.suggestion)