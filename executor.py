import re
import sys
import subprocess
import tempfile
import os
from lexer import Lexer, LexerError
from parser import Parser
from semantic import SemanticAnalyzer, SemanticError
from codegen import CodeGenerator, CodeGenError

if not hasattr(CodeGenerator, '_decorators'):
    print("ERROR: You're using the OLD broken codegen.py")
    print("Please replace it with the fixed version.")
    print("The fixed codegen.py should have the '_decorators' attribute.")
    sys.exit(1)

_RUNTIME_UNSAFE = {
    r'\bopen\s*\(':          "file I/O (open)",
    r'\btkinter\b':          "tkinter GUI",
    r'\bsubprocess\b':       "subprocess",
    r'\bthreading\b':        "threading",
    r'\bsocket\b':           "socket",
    r'\basyncio\b':          "asyncio",
    r'\bos\.system\s*\(':    "os.system",
}


def check_runtime_unsafe(source_code):
    found = []
    for pattern, name in _RUNTIME_UNSAFE.items():
        if re.search(pattern, source_code) and name not in found:
            found.append(name)
    return found


def get_js_code(source_code):
    tokens = Lexer(source_code).tokenize()
    ast    = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    return CodeGenerator().generate(ast)


def extract_input_prompts(source_code):
    prompts = []
    for match in re.finditer(r'\binput\s*\(([^)]*)\)', source_code):
        inner = match.group(1).strip()
        str_match = re.match(r'^["\'](.+?)["\']$', inner)
        if str_match:
            prompts.append(str_match.group(1).rstrip(": ").strip())
        else:
            prompts.append(None)
    return prompts


def collect_user_inputs(source_code):
    prompts = extract_input_prompts(source_code)
    if not prompts:
        return []
    print(f"\n[ This program requires {len(prompts)} input value(s) ]")
    print("-" * 30)
    values = []
    for i, prompt in enumerate(prompts, 1):
        label = prompt if prompt else f"Input {i}"
        val   = input(f"  {label}: ")
        values.append(val)
    return values


def run_python(source_code, user_inputs):
    stdin_data = "\n".join(user_inputs) + ("\n" if user_inputs else "")
    try:
        result = subprocess.run(
            [sys.executable, "-c", source_code],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            err = result.stderr.strip().splitlines()
            return f"[Runtime Error] {err[-1]}" if err else "[Runtime Error] Unknown"
        return result.stdout.rstrip("\n")
    except subprocess.TimeoutExpired:
        return "[Error] Python execution timed out."
    except Exception as e:
        return f"[Error] {str(e)}"


def run_js(js_code, user_inputs):
    inputs_js = "[" + ", ".join(f'"{v}"' for v in user_inputs) + "]"
    shim = (
        f"const _inputs = {inputs_js};\n"
        f"let _inputIndex = 0;\n"
        f"\n"
        f"// Shim for Python input() -> JavaScript prompt()\n"
        f"function prompt(msg) {{\n"
        f"  // Match Python input() behavior:\n"
        f"  // - Show prompt with newline\n"
        f"  // - Return value from input array\n"
        f"  if (msg) {{\n"
        f"    process.stdout.write(msg);\n"
        f"  }}\n"
        f"  return _inputs[_inputIndex++] || '';\n"
        f"}}\n"
        f"\n"
    )
    full_js  = shim + js_code
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".js", delete=False, encoding="utf-8"
        ) as f:
            f.write(full_js)
            tmp_path = f.name
        result = subprocess.run(
            ["node", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            stderr = result.stderr.strip()
            if stderr:
                lines = stderr.splitlines()
                for line in lines:
                    if "Error" in line or "error" in line:
                        return f"[JS Runtime Error] {line.strip()}"
                return f"[JS Runtime Error] {lines[-1]}" if lines else "[JS Runtime Error] Unknown"
            return "[JS Runtime Error] Unknown error (no stderr)"
        return result.stdout.rstrip("\n")
    except FileNotFoundError:
        return "[Error] Node.js is not installed or not found in PATH."
    except subprocess.TimeoutExpired:
        return "[Error] JS execution timed out (>10 seconds)."
    except Exception as e:
        return f"[Error] {str(e)}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass  


def _normalize(text):
    return re.sub(r'(-?\d+)\.0\b', r'\1', text)


def run_executor(source_code):
    print("\n" + "=" * 50)
    print("         OUTPUT COMPARISON")
    print("=" * 50)

    unsafe = check_runtime_unsafe(source_code)
    if unsafe:
        print("\n[ RUNTIME WARNING ]")
        print("-" * 30)
        for feature in unsafe:
            print(f"  ⚠  '{feature}' may not run correctly in the JS shim.")
        print("  Output comparison may be unreliable for this code.\n")

    try:
        js_code = get_js_code(source_code)
    except LexerError as e:
        print(f"\n[Lexer Error] line {e.line}, col {e.column}: {e.message}")
        if e.suggestion:
            print("Suggestion:", e.suggestion)
        print("=" * 50)
        return
    except SemanticError as e:
        print(f"\n[Semantic Error] {e}")
        print("=" * 50)
        return
    except CodeGenError as e:
        print(f"\n[Code Generation Error] {e}")
        print("  This construct is recognised by the parser but not yet")
        print("  supported by the code generator.")
        print("=" * 50)
        return
    except Exception as e:
        print(f"\n[Unexpected Transpiler Error] {e}")
        print("=" * 50)
        return

    user_inputs = collect_user_inputs(source_code)
    print("\n[ PYTHON OUTPUT ]")
    print("-" * 30)
    py_output = run_python(source_code, user_inputs)
    print(py_output if py_output else "(no output)")

    print("\n[ JAVASCRIPT OUTPUT ]")
    print("-" * 30)
    js_output = run_js(js_code, user_inputs)
    print(js_output if js_output else "(no output)")

    print("\n" + "=" * 50)
    py_norm = _normalize(py_output)
    js_norm = _normalize(js_output)
    
    if py_norm == js_norm:
        print("✔  Both outputs MATCH — transpilation is correct!")
    else:
        print("✘  Outputs DO NOT match — check transpilation logic.")
        print(f"   Python : {repr(py_output)}")
        print(f"   JS     : {repr(js_output)}")
    print("=" * 50)

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
        run_executor(source_code)
    except LexerError as e:
        print(f"\nLexer Error at line {e.line}, column {e.column}: {e.message}")
        if e.suggestion:
            print("Suggestion:", e.suggestion)
    except SemanticError as e:
        print("Semantic Error:", e)
    except CodeGenError as e:
        print("Code Generation Error:", e)
    except Exception as e:
        print("Unexpected Error:", e)