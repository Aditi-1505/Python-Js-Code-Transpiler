from transpiler import run_transpiler
from executor import run_executor
from lexer import LexerError, Lexer
from semantic import SemanticError, SemanticAnalyzer
from codegen import CodeGenError
from parser import Parser, FunctionDef, ClassDef, Import, FromImport, Program


def _has_runnable_statements(source_code):
    try:
        tokens = Lexer(source_code).tokenize()
        ast    = Parser(tokens).parse()
        for stmt in ast.statements:
            if not isinstance(stmt, (FunctionDef, ClassDef, Import, FromImport)):
                return True
        return False
    except Exception:
        return True  

def launch_visualizer(source_code):
    try:
        import tkinter as tk
        from visualize import ASTVisualizerApp
    except ImportError as e:
        print(f"\n[Visualizer] Could not import required module: {e}")
        return

    try:
        # Pass source_code directly — ASTVisualizerApp will pre-load the code
        # and schedule draw_tree via after() so the canvas is fully sized first.
        app = ASTVisualizerApp(source_code=source_code)
        app.bind("<Control-Return>", lambda e: app._run())
        app.mainloop()
    except Exception as e:
        print(f"\n[Visualizer] Error: {e}")


if __name__ == "__main__":
    print("\nEnter Python code (press Enter twice to finish):\n")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    source_code = "\n".join(lines)

    try:
        run_transpiler(source_code)
        if _has_runnable_statements(source_code):
            run_executor(source_code)
        else:
            print("\n[ OUTPUT COMPARISON SKIPPED ]")
            print("-" * 50)
            print("  No top-level runnable statements found.")
            print("  (Code only defines functions/classes — nothing to execute)")
            print("-" * 50)

    except LexerError as e:
        print(f"\nLexer Error  line {e.line}, col {e.column}")
        print(e.message)
        if e.suggestion:
            print("Suggestion:", e.suggestion)
    except SemanticError as e:
        print("Semantic Error:", e)
    except CodeGenError as e:
        print("Code Generation Error:", e)
    except Exception as e:
        print("Unexpected Error:", e)
    finally:
        launch_visualizer(source_code)