from lexer import Lexer, LexerError, TokenType
from parser import Parser, print_ast
from semantic import SemanticAnalyzer, SemanticError
from codegen import CodeGenerator, CodeGenError
from symbol_table import SymbolTableGenerator, print_symbol_table


def print_tokens(tokens):
    print(f"{'TYPE':<25} {'VALUE':<20} LINE")
    print("-" * 55)
    for token in tokens:
        if token.type not in (TokenType.EOF, TokenType.COMMENT):
            print(f"{token.type.name:<25} {repr(token.value):<20} {token.line}")


def run_transpiler(source_code):
    print("\n" + "=" * 55)
    print("  PYTHON → JAVASCRIPT TRANSPILER")
    print("=" * 55)

    print("\n" + "-" * 55)
    print("  STAGE 1 — LEXICAL ANALYSIS  (TOKENS)")
    print("-" * 55)
    lexer  = Lexer(source_code)
    tokens = lexer.tokenize()
    print_tokens(tokens)

    print("\n" + "-" * 55)
    print("  STAGE 2 — SYNTAX ANALYSIS  (AST)")
    print("-" * 55)
    parser = Parser(tokens)
    ast    = parser.parse()
    print_ast(ast)

    print("\n" + "-" * 55)
    print("  STAGE 3 — SYMBOL TABLE GENERATION")
    print("-" * 55)
    generator = SymbolTableGenerator()
    table     = generator.generate(ast)
    print_symbol_table(table)

    print("\n" + "-" * 55)
    print("  STAGE 4 — SEMANTIC ANALYSIS")
    print("-" * 55)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    print("✔  No semantic errors found")

    print("\n" + "-" * 55)
    print("  STAGE 5 — CODE GENERATION  (JavaScript)")
    print("-" * 55)
    codegen = CodeGenerator()
    js_code = codegen.generate(ast)
    print("\nGenerated JavaScript:\n")
    print(js_code)

    print("\n" + "=" * 55)
    print("  COMPILATION COMPLETED SUCCESSFULLY")
    print("=" * 55)

    return js_code