import os, re, sys
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, BASE_DIR)

from lexer import Lexer, LexerError
from parser import Parser, Program
from semantic import SemanticAnalyzer, SemanticError
from codegen import CodeGenerator, CodeGenError
from symbol_table import SymbolTableGenerator

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")


# ---------------------------------------------------------------------------

_PY_TO_JS = {"Number": "NumberNode", "String": "StringNode"}

def _ast_to_dict(node):
    if node is None:
        return None
    if isinstance(node, list):
        return [_ast_to_dict(n) for n in node]

    cls = type(node).__name__
    t   = _PY_TO_JS.get(cls, cls)
    d   = {"type": t}
    a   = _ast_to_dict   # shorthand

    if cls in ("Number", "String", "FString", "BoolLiteral"):
        d["value"] = node.value
    elif cls == "NoneLiteral":
        pass  # no extra fields
    elif cls == "Identifier":
        d["name"] = node.name

    elif cls in ("ListLiteral", "TupleLiteral", "SetLiteral"):
        d["elements"] = [a(e) for e in node.elements]
    elif cls == "DictLiteral":
        d["pairs"] = [[a(k), a(v)] for k, v in node.pairs]
    elif cls == "ListComp":
        d["elt"]    = a(node.elt)
        d["target"] = node.target
        d["iter_"]  = a(node.iter_)
        d["cond"]   = a(node.cond) if node.cond else None

    elif cls == "Attribute":
        d["value"] = a(node.value)
        d["attr"]  = node.attr
    elif cls == "Subscript":
        d["value"] = a(node.value)
        d["index"] = a(node.index)
    elif cls == "Slice":
        d["lower"] = a(node.lower) if node.lower else None
        d["upper"] = a(node.upper) if node.upper else None
        d["step"]  = a(node.step)  if node.step  else None

    elif cls == "BinaryOp":
        d["left"]  = a(node.left)
        d["op"]    = {"name": node.op.name, "value": node.op.value}
        d["right"] = a(node.right)
    elif cls == "UnaryOp":
        d["op"]      = str(node.op)
        d["operand"] = a(node.operand)
    elif cls == "BoolOp":
        d["op"]     = str(node.op)
        d["values"] = [a(v) for v in node.values]
    elif cls == "Ternary":
        d["body"]   = a(node.body)
        d["test"]   = a(node.test)
        d["orelse"] = a(node.orelse)
    elif cls == "Lambda":
        d["params"] = node.params
        d["body"]   = a(node.body)
    elif cls == "FunctionCall":
        d["name"]   = node.name
        d["args"]   = [a(x) for x in node.args]
        d["kwargs"] = {k: a(v) for k, v in (node.kwargs or {}).items()}
    elif cls == "MethodCall":
        d["obj"]    = a(node.obj)
        d["method"] = node.method
        d["args"]   = [a(x) for x in node.args]
        d["kwargs"] = {k: a(v) for k, v in (node.kwargs or {}).items()}

    elif cls == "Program":
        d["statements"] = [a(s) for s in node.statements]
    elif cls == "Assignment":
        d["name"]  = node.name if isinstance(node.name, str) else a(node.name)
        d["value"] = a(node.value)
    elif cls == "ComplexAssignment":
        d["target"] = a(node.target)
        d["value"]  = a(node.value)
    elif cls == "AugmentedAssignment":
        d["target"] = a(node.target)
        d["op"]     = {"name": node.op.name, "value": node.op.value}
        d["value"]  = a(node.value)
    elif cls == "Print":
        d["expression"] = a(node.expression)
    elif cls == "Return":
        d["value"] = a(node.value) if node.value else None
    elif cls == "Raise":
        d["exc"] = a(node.exc) if node.exc else None
    elif cls == "Delete":
        d["targets"] = [a(x) for x in node.targets]
    elif cls == "Assert":
        d["test"] = a(node.test)
        d["msg"]  = a(node.msg) if node.msg else None
    elif cls in ("Pass", "Break", "Continue"):
        pass  # no extra fields
    elif cls in ("Global", "Nonlocal"):
        d["names"] = node.names

    elif cls == "If":
        d["condition"]    = a(node.condition)
        d["body"]         = [a(s) for s in node.body]
        d["elif_clauses"] = [[a(c), [a(s) for s in b]] for c, b in node.elif_clauses]
        d["else_body"]    = [a(s) for s in (node.else_body or [])]
    elif cls == "While":
        d["condition"] = a(node.condition)
        d["body"]      = [a(s) for s in node.body]
    elif cls == "For":
        d["var"]   = node.var
        d["start"] = a(node.start)
        d["stop"]  = a(node.stop)
        d["step"]  = a(node.step) if node.step else None
        d["body"]  = [a(s) for s in node.body]
    elif cls == "ForIn":
        d["var"]      = node.var
        d["iterable"] = a(node.iterable)
        d["body"]     = [a(s) for s in node.body]
    elif cls == "With":
        d["expr"]  = a(node.expr)
        d["alias"] = node.alias
        d["body"]  = [a(s) for s in node.body]

    elif cls == "FunctionDef":
        d["name"]       = node.name
        d["params"]     = node.params
        d["body"]       = [a(s) for s in node.body]
        d["defaults"]   = {k: a(v) for k, v in (node.defaults or {}).items()}
        d["vararg"]     = node.vararg
        d["kwarg"]      = node.kwarg
        d["decorators"] = list(node.decorators or [])
    elif cls == "ClassDef":
        d["name"]       = node.name
        d["bases"]      = list(node.bases or [])
        d["body"]       = [a(s) for s in node.body]
        d["decorators"] = list(node.decorators or [])

    elif cls == "TryExcept":
        d["body"]       = [a(s) for s in node.body]
        d["handlers"]   = [a(s) for s in node.handlers]
        d["else_body"]  = [a(s) for s in (node.else_body  or [])]
        d["final_body"] = [a(s) for s in (node.final_body or [])]
    elif cls == "ExceptHandler":
        d["exc_type"] = node.exc_type
        d["name"]     = node.name
        d["body"]     = [a(s) for s in node.body]

    elif cls == "Import":
        d["names"] = node.names
    elif cls == "FromImport":
        d["module"] = node.module
        d["names"]  = node.names

    return d

def _token_to_dict(tok):
    return {
        "type": tok.type.name,
        "value": tok.value,
        "line": tok.line,
        "column": tok.column
    }

_RUNTIME_UNSAFE = {
    r"\bopen\s*\(":       "file I/O (open)",
    r"\btkinter\b":       "tkinter GUI",
    r"\bsubprocess\b":    "subprocess",
    r"\bthreading\b":     "threading",
    r"\bsocket\b":        "socket",
    r"\basyncio\b":       "asyncio",
    r"\bos\.system\s*\(": "os.system",
}

def _check_unsupported(src):
    """Return features that may not execute correctly in the Node.js shim."""
    found = []
    for pat, name in _RUNTIME_UNSAFE.items():
        if re.search(pat, src) and name not in found:
            found.append(name)
    return found


@app.route("/")
def index():
    return send_from_directory(WEB_DIR, "app.html")


@app.route("/transpiler.js")
def transpiler_js():
    return send_from_directory(WEB_DIR, "transpiler.js")


@app.route("/api/transpile", methods=["POST"])
def transpile():
    data   = request.get_json(force=True, silent=True) or {}
    source = data.get("source", "")
    if not source.strip():
        return jsonify({"error": "No source code provided"}), 400
    result = {
        "tokens": None,
        "ast": None,
        "symbolTable": None,
        "jsCode": None,
        "error": None,
        "unsupported": _check_unsupported(source),
    }
    try:
        tokens = Lexer(source).tokenize()
        result["tokens"] = [_token_to_dict(t) for t in tokens]
    except LexerError as e:
        result["error"] = {
            "stage": "Lexer",
            "message": e.message,
            "line": e.line,
            "col": e.column,
        }
        return jsonify(result)
    try:
        ast = Parser(tokens).parse()
        result["ast"] = _ast_to_dict(ast)
    except Exception as e:
        result["error"] = {"stage": "Parser", "message": str(e)}
        return jsonify(result)
    try:
        result["symbolTable"] = SymbolTableGenerator().generate(ast)
    except:
        pass

    try:
        SemanticAnalyzer().analyze(ast)
    except SemanticError as e:
        result["error"] = {"stage": "Semantic", "message": str(e)}
        return jsonify(result)

    try:
        result["jsCode"] = CodeGenerator().generate(ast)
    except CodeGenError as e:
        result["error"] = {"stage": "CodeGen", "message": str(e)}
        return jsonify(result)

    return jsonify(result)


@app.route("/api/execute", methods=["POST"])
def execute():
    import subprocess, tempfile, os, re as _re

    data   = request.get_json(force=True, silent=True) or {}
    source = data.get("source", "")
    inputs = data.get("inputs", [])

    if not source.strip():
        return jsonify({"error": "No source code provided"}), 400

    stdin_data = "\n".join(str(v) for v in inputs) + ("\n" if inputs else "")

    try:
        py_result = subprocess.run(
            [sys.executable, "-c", source],
            input=stdin_data, capture_output=True, text=True, timeout=10,
        )
        if py_result.returncode != 0:
            err_lines = py_result.stderr.strip().splitlines()
            py_output = f"[Runtime Error] {err_lines[-1]}" if err_lines else "[Runtime Error] Unknown"
        else:
            py_output = py_result.stdout.rstrip("\n")
    except subprocess.TimeoutExpired:
        py_output = "[Error] Python execution timed out."
    except Exception as e:
        py_output = f"[Error] {str(e)}"

    js_output = ""
    js_code = None
    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        SemanticAnalyzer().analyze(ast)
        js_code = CodeGenerator().generate(ast)
    except Exception as e:
        js_output = f"[Transpiler Error] {str(e)}"

    if js_code:
        inputs_js = "[" + ", ".join(f'"{v}"' for v in inputs) + "]"
        shim = (
            "const _inputs = " + inputs_js + ";\n"
            "let _inputIndex = 0;\n"
            "function prompt(msg) {\n"
            "  if (msg) process.stdout.write(msg);\n"
            "  return _inputs[_inputIndex++] || '';\n"
            "}\n"
        )
        full_js  = shim + js_code
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False, encoding="utf-8"
            ) as f:
                f.write(full_js)
                tmp_path = f.name
            js_result = subprocess.run(
                ["node", tmp_path],
                capture_output=True, text=True, timeout=10, encoding="utf-8"
            )
            if js_result.returncode != 0:
                stderr = js_result.stderr.strip()
                lines  = stderr.splitlines() if stderr else []
                js_output = next(
                    (f"[JS Runtime Error] {l.strip()}" for l in lines if "Error" in l or "error" in l),
                    f"[JS Runtime Error] {lines[-1]}" if lines else "[JS Runtime Error] Unknown"
                )
            else:
                js_output = js_result.stdout.rstrip("\n")
        except FileNotFoundError:
            js_output = "[Error] Node.js is not installed or not in PATH."
        except subprocess.TimeoutExpired:
            js_output = "[Error] JS execution timed out."
        except Exception as e:
            js_output = f"[Error] {str(e)}"
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try: os.remove(tmp_path)
                except Exception: pass

    def _norm(t):
        t = _re.sub(r'(-?\d+)\.0\b', r'\1', t)       
        t = _re.sub(r'\[\s+', '[', t)                  
        t = _re.sub(r'\s+\]', ']', t)                  
        t = _re.sub(r',\s+', ', ', t)                  
        t = _re.sub(r'\s+', ' ', t).strip()            
        return t

    return jsonify({
        "py_output":   py_output,
        "js_output":   js_output,
        "match":       _norm(py_output) == _norm(js_output),
        "unsupported": _check_unsupported(source),
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
