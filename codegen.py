import re
from parser import (
    Program, Number, String, FString, BoolLiteral, NoneLiteral,
    Identifier, Attribute, Subscript, Slice,
    BinaryOp, UnaryOp, BoolOp, Ternary, Lambda,
    FunctionCall, MethodCall, ListComp,
    ListLiteral, DictLiteral, TupleLiteral, SetLiteral,
    Assignment, ComplexAssignment, AugmentedAssignment,
    Print, Return, Raise, Delete, Assert, Pass, Break, Continue,
    Global, Nonlocal,
    If, While, For, ForIn, With,
    FunctionDef, ClassDef,
    TryExcept, ExceptHandler,
    Import, FromImport,
)

_OP_MAP = {
    "PLUS":           "+",   "MINUS":          "-",
    "MULTIPLY":       "*",   "DIVIDE":         "/",
    "MODULO":         "%",   "FLOOR_DIVIDE":   "//",
    "POWER":          "**",
    "DOUBLE_EQUALS":  "===", "NOT_EQUALS":     "!==",
    "LESS_THAN":      "<",   "GREATER_THAN":   ">",
    "LESS_EQUAL":     "<=",  "GREATER_EQUAL":  ">=",
    "AND":            "&&",  "OR":             "||",
    "BITWISE_AND":    "&",   "BITWISE_OR":     "|",
    "BITWISE_XOR":    "^",   "LSHIFT":         "<<",
    "RSHIFT":         ">>",
    "IN":             None,  
    "IS":             "===", "IS_NOT":         "!==",
}

_BUILTIN_MAP = {
    "print":    "console.log",
    "len":      None,         
    "int":      None,          
    "float":    "parseFloat",
    "str":      "String",
    "bool":     "Boolean",
    "list":     "Array.from",
    "dict":     None,          
    "set":      None,         
    "tuple":    "Array.from",
    "abs":      "Math.abs",
    "max":      "Math.max",
    "min":      "Math.min",
    "round":    "Math.round",
    "pow":      "Math.pow",
    "sorted":   None,          
    "reversed": None,          
    "sum":      None,          
    "any":      None,          
    "all":      None,         
    "enumerate":None,         
    "zip":      None,          
    "map":      None,          
    "filter":   None,          
    "isinstance":None,        
    "hasattr":  None,          
    "getattr":  None,          
    "setattr":  None,         
    "type":     "typeof",
    "id":       None,          
    "repr":     None,          
    "chr":      "String.fromCharCode",
    "ord":      None,          
    "hex":      None,          
    "oct":      None,          
    "bin":      None,          
    "input":    "prompt",
    "range":    None,          
    "Exception":          "Error",
    "ValueError":         "Error",
    "TypeError":          "TypeError",
    "KeyError":           "Error",
    "IndexError":         "Error",
    "AttributeError":     "Error",
    "NameError":          "ReferenceError",
    "RuntimeError":       "Error",
    "NotImplementedError":"Error",
    "AssertionError":     "Error",
    "ZeroDivisionError":  "Error",
    "StopIteration":      "Error",
    "OSError":            "Error",
    "IOError":            "Error",
    "FileNotFoundError":  "Error",
    "word":    "String",
    "largest": "Math.max",
    "least":   "Math.min",
    "sqrt":    "Math.sqrt",
}

_METHOD_MAP = {
    "append":    "push",
    "extend":    None,      
    "index":     "indexOf",
    "count":     None,       
    "copy":      None,       
    "clear":     None,       
    "upper":     "toUpperCase",
    "lower":     "toLowerCase",
    "strip":     "trim",
    "lstrip":    "trimStart",
    "rstrip":    "trimEnd",
    "startswith":"startsWith",
    "endswith":  "endsWith",
    "find":      "indexOf",
    "rfind":     "lastIndexOf",
    "replace":   "replace",
    "split":     "split",
    "join":      None,       
    "encode":    None,       
    "decode":    None,       
    "format":    None,       
    "keys":      None,       
    "values":    None,       
    "items":     None,       
    "get":       None,       
    "update":    None,       
    "pop":       "pop",
    "popitem":   None,
    "setdefault":None,
    "sort":      "sort",
    "reverse":   "reverse",
    "insert":    None,       
    "remove":    None,       
    "discard":   None,
    "add":       None,       
    "isdigit":   None,       
    "isalpha":   None,
    "isalnum":   None,
}

class CodeGenError(Exception):
    pass


def _collect_assigned(stmts):
    names = set()
    for node in stmts:
        if isinstance(node, Assignment):
            names.add(node.name)
        elif isinstance(node, If):
            names |= _collect_assigned(node.body)
            for _, b in node.elif_clauses:
                names |= _collect_assigned(b)
            if node.else_body:
                names |= _collect_assigned(node.else_body)
        elif isinstance(node, While):
            names |= _collect_assigned(node.body)
        elif isinstance(node, TryExcept):
            names |= _collect_assigned(node.body)
            for h in node.handlers:
                names |= _collect_assigned(h.body)
    return names


class CodeGenerator:
    _decorators = {}   

    def __init__(self, indent_size=2):
        self._indent_size = indent_size
        self._level       = 0
        self._declared    = set()    
        self._in_class    = False    
        self._class_stack = []       
        self._class_names = set()    
        self._decorators  = {}      
        self._in_function = False    
        self._function_params = {}   

    @property
    def pad(self):
        return " " * (self._indent_size * self._level)
    
    def indent(self):  
        self._level += 1
    
    def dedent(self):  
        self._level -= 1

    def generate(self, node):
        if not isinstance(node, Program):
            raise CodeGenError(f"Expected Program, got {type(node).__name__}")
        
        for stmt in node.statements:
            if isinstance(stmt, ClassDef):
                self._class_names.add(stmt.name)
            elif isinstance(stmt, FunctionDef):
                if stmt.decorators:
                    self._decorators[stmt.name] = stmt.decorators
        
        lines = []
        for stmt in node.statements:
            lines.extend(self.gen_stmt(stmt))
        
        return "\n".join(lines)

    def gen_stmt(self, node):
        if isinstance(node, Assignment):       
            return self.gen_assignment(node)
        if isinstance(node, ComplexAssignment):
            return self.gen_complex_assign(node)
        if isinstance(node, AugmentedAssignment): 
            return self.gen_aug_assign(node)
        if isinstance(node, Print):            
            return [f"{self.pad}console.log({self.gen_expr(node.expression)});"]
        if isinstance(node, Return):           
            return self.gen_return(node)
        if isinstance(node, Raise):            
            return self.gen_raise(node)
        if isinstance(node, Delete):           
            return self.gen_delete(node)
        if isinstance(node, Assert):           
            return self.gen_assert(node)
        if isinstance(node, Pass):             
            return [f"{self.pad}// pass"]
        if isinstance(node, Break):            
            return [f"{self.pad}break;"]
        if isinstance(node, Continue):         
            return [f"{self.pad}continue;"]
        if isinstance(node, Global):           
            return [f"{self.pad}// global {', '.join(node.names)}"]
        if isinstance(node, Nonlocal):         
            return [f"{self.pad}// nonlocal {', '.join(node.names)}"]
        if isinstance(node, If):               
            return self.gen_if(node)
        if isinstance(node, While):            
            return self.gen_while(node)
        if isinstance(node, For):              
            return self.gen_for(node)
        if isinstance(node, ForIn):            
            return self.gen_for_in(node)
        if isinstance(node, With):             
            return self.gen_with(node)
        if isinstance(node, FunctionDef):      
            return self.gen_function_def(node)
        if isinstance(node, ClassDef):         
            return self.gen_class_def(node)
        if isinstance(node, TryExcept):        
            return self.gen_try(node)
        if isinstance(node, Import):           
            return self.gen_import(node)
        if isinstance(node, FromImport):       
            return self.gen_from_import(node)
        if isinstance(node, (FunctionCall, MethodCall)):
            return [f"{self.pad}{self.gen_expr(node)};"]
        if isinstance(node, BinaryOp):
            return [f"{self.pad}{self.gen_expr(node)};"]
        if isinstance(node, UnaryOp):
            return [f"{self.pad}{self.gen_expr(node)};"]
        if isinstance(node, ListComp):
            return [f"{self.pad}{self.gen_expr(node)};"]
        raise CodeGenError(f"Unknown statement node: {type(node).__name__}")

    def gen_assignment(self, node):
        val = self.gen_expr(node.value)
        if node.name not in self._declared:
            self._declared.add(node.name)
            return [f"{self.pad}let {node.name} = {val};"]
        return [f"{self.pad}{node.name} = {val};"]

    def gen_complex_assign(self, node):
        target = self.gen_expr(node.target)
        val    = self.gen_expr(node.value)
        return [f"{self.pad}{target} = {val};"]

    def gen_aug_assign(self, node):
        target = self.gen_expr(node.target)
        val    = self.gen_expr(node.value)
        if node.op == "//=":
            return [f"{self.pad}{target} = Math.floor({target} / {val});"]
        return [f"{self.pad}{target} {node.op} {val};"]

    def gen_return(self, node):
        if node.value is None:
            return [f"{self.pad}return;"]
        return [f"{self.pad}return {self.gen_expr(node.value)};"]

    def gen_raise(self, node):
        if node.exc is None:
            return [f"{self.pad}throw new Error();"]
        exc_js = self.gen_expr(node.exc)
        return [f"{self.pad}throw {exc_js};"]

    def gen_delete(self, node):
        lines = []
        for t in node.targets:
            lines.append(f"{self.pad}delete {self.gen_expr(t)};")
        return lines

    def gen_assert(self, node):
        test = self.gen_expr(node.test)
        if node.msg:
            msg = self.gen_expr(node.msg)
            return [f"{self.pad}if (!({test})) {{ throw new Error({msg}); }}"]
        return [f"{self.pad}console.assert({test});"]

    def gen_if(self, node):
        lines = []
        all_bodies = ([node.body]
                      + [b for _, b in node.elif_clauses]
                      + ([node.else_body] if node.else_body else []))
        for body in all_bodies:
            for name in _collect_assigned(body):
                if name not in self._declared:
                    self._declared.add(name)
                    lines.append(f"{self.pad}let {name};")

        cond = self.gen_expr(node.condition)
        lines.append(f"{self.pad}if ({cond}) {{")
        lines.extend(self.gen_block(node.body))
        for elif_cond, elif_body in node.elif_clauses:
            ec = self.gen_expr(elif_cond)
            lines.append(f"{self.pad}}} else if ({ec}) {{")
            lines.extend(self.gen_block(elif_body))
        if node.else_body:
            lines.append(f"{self.pad}}} else {{")
            lines.extend(self.gen_block(node.else_body))
        lines.append(f"{self.pad}}}")
        return lines

    def gen_while(self, node):
        cond  = self.gen_expr(node.condition)
        lines = [f"{self.pad}while ({cond}) {{"]
        lines.extend(self.gen_block(node.body))
        lines.append(f"{self.pad}}}")
        return lines

    def gen_for(self, node):
        var   = node.var
        start = self.gen_expr(node.start)
        stop  = self.gen_expr(node.stop)
        decl  = "let " if var not in self._declared else ""
        self._declared.add(var)
        
        if node.step is None:
            header = f"for ({decl}{var} = {start}; {var} < {stop}; {var}++)"
        else:
            step = self.gen_expr(node.step)
            if isinstance(node.step, Number):
                is_neg = float(node.step.value) < 0
                cmp_op = ">" if is_neg else "<"
                header = f"for ({decl}{var} = {start}; {var} {cmp_op} {stop}; {var} += {step})"
            elif isinstance(node.step, UnaryOp) and node.step.op == "-":
                header = f"for ({decl}{var} = {start}; {var} > {stop}; {var} += {step})"
            else:
                header = (
                    f"for ({decl}{var} = {start}; "
                    f"({step} > 0 ? {var} < {stop} : {var} > {stop}); "
                    f"{var} += {step})"
                )
        lines = [f"{self.pad}{header} {{"]
        lines.extend(self.gen_block(node.body))
        lines.append(f"{self.pad}}}")
        return lines

    def gen_for_in(self, node):
        iter_js = self.gen_expr(node.iterable)
        if isinstance(node.var, list):
            for v in node.var:
                self._declared.add(v)
            var_js = "[" + ", ".join(node.var) + "]"
            lines = [f"{self.pad}for (let {var_js} of {iter_js}) {{"]
        else:
            var  = node.var
            decl = "let " if var not in self._declared else ""
            self._declared.add(var)
            lines = [f"{self.pad}for ({decl}{var} of {iter_js}) {{"]
        lines.extend(self.gen_block(node.body))
        lines.append(f"{self.pad}}}")
        return lines

    def gen_with(self, node):
        lines = [f"{self.pad}{{  // with {self.gen_expr(node.expr)}"]
        if node.alias:
            if node.alias not in self._declared:
                self._declared.add(node.alias)
                lines.insert(0, f"{self.pad}let {node.alias} = {self.gen_expr(node.expr)};")
            else:
                lines.insert(0, f"{self.pad}{node.alias} = {self.gen_expr(node.expr)};")
            lines[1] = f"{self.pad}{{  // with ... as {node.alias}"
        lines.extend(self.gen_block(node.body))
        lines.append(f"{self.pad}}}")
        return lines

    def gen_function_def(self, node):
        lines = []
        for d in node.decorators:
            lines.append(f"{self.pad}// @{d}")
        
        params = list(node.params)
    
        if self._in_class and params and params[0] == "self":
            params = params[1:]
       
        param_parts = []
        for p in params:
            if p in node.defaults:
                param_parts.append(f"{p} = {self.gen_expr(node.defaults[p])}")
            else:
                param_parts.append(p)
        
        if node.vararg:
            param_parts.append(f"...{node.vararg}")
        
        has_kwargs = bool(node.kwarg)
        if has_kwargs:
            param_parts.append(f"...__kwargs")
        
        param_str = ", ".join(param_parts)
        
        if self._in_class:
            fn_name = "constructor" if node.name == "__init__" else node.name
            header  = f"{self.pad}{fn_name}({param_str}) {{"
        else:
            header = f"{self.pad}function {node.name}({param_str}) {{"
        lines.append(header)
        saved_declared = self._declared
        saved_in_class = self._in_class
        saved_in_function = self._in_function
        
        self._declared = set(params)
        if node.vararg:
            self._declared.add(node.vararg)
        if has_kwargs:
            self.indent()
            self._declared.add(node.kwarg)
            lines.append(f"{self.pad}let {node.kwarg} = Object.assign({{}}, ...__kwargs);")
            self.dedent()
        
        self._in_class = False
        self._in_function = True
        
        lines.extend(self.gen_block(node.body))
        
        self._declared = saved_declared
        self._in_class = saved_in_class
        self._in_function = saved_in_function
        
        lines.append(f"{self.pad}}}")
        if node.decorators:
            for decorator in reversed(node.decorators):
                fn_name = node.name
                lines.append(f"{self.pad}{fn_name} = {decorator}({fn_name});")
        
        return lines

    def gen_class_def(self, node):
        lines = []
        for d in node.decorators:
            lines.append(f"{self.pad}// @{d}")
        if node.bases:
            if len(node.bases) > 1:
                raise CodeGenError(
                    f"JavaScript does not support multiple inheritance. "
                    f"Class {node.name} cannot extend {', '.join(node.bases)}. "
                    f"Use composition or mixins instead."
                )
            base_js = node.bases[0]
            lines.append(f"{self.pad}class {node.name} extends {base_js} {{")
        else:
            lines.append(f"{self.pad}class {node.name} {{")
        
        saved_declared = self._declared
        saved_in_class = self._in_class
        self._declared = set()
        self._in_class = True
        self._class_stack.append(node.name)
        self.indent()
        static_props = {}
        
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                lines.extend(self.gen_function_def(stmt))
            elif isinstance(stmt, Assignment):
                static_props[stmt.name] = stmt.value
                lines.append(
                    f"{self.pad}static {stmt.name} = {self.gen_expr(stmt.value)};"
                )
            elif isinstance(stmt, Pass):
                lines.append(f"{self.pad}// pass")
            else:
                lines.extend(self.gen_stmt(stmt))
        
        self.dedent()
        self._class_stack.pop()
        self._declared = saved_declared
        self._in_class = saved_in_class
        lines.append(f"{self.pad}}}")
        
        return lines

    def gen_try(self, node):
        lines = [f"{self.pad}try {{"]
        lines.extend(self.gen_block(node.body))
        
        if node.handlers:
            catch_var = None
            for h in node.handlers:
                if h.name:
                    catch_var = h.name
                    break
            catch_var = catch_var or "_e"
            
            lines.append(f"{self.pad}}} catch ({catch_var}) {{")
            self.indent()
            first = True
            for h in node.handlers:
                if h.exc_type:
                    js_exc = _BUILTIN_MAP.get(h.exc_type, h.exc_type)
                    
                    if h.exc_type == "ValueError":
                        kw = "if" if first else "else if"
                        lines.append(f"{self.pad}{kw} ({catch_var} instanceof Error) {{")
                    else:
                        kw = "if" if first else "else if"
                        lines.append(f"{self.pad}{kw} ({catch_var} instanceof {js_exc}) {{")
                    
                    if h.name and h.name != catch_var:
                        lines.append(f"{self.pad}  let {h.name} = {catch_var};")
                    
                    lines.extend(self.gen_block(h.body))
                    lines.append(f"{self.pad}}}")
                    first = False
                else:
                    if not first:
                        lines.append(f"{self.pad}else {{")
                    lines.extend(self.gen_block(h.body))
                    if not first:
                        lines.append(f"{self.pad}}}")
                    first = False
            
            self.dedent()
            lines.append(f"{self.pad}}}")
        else:
            lines.append(f"{self.pad}}}")
        
        if node.final_body:
            lines.append(f"{self.pad}finally {{")
            lines.extend(self.gen_block(node.final_body))
            lines.append(f"{self.pad}}}")
        
        if node.else_body:
            lines.append(f"{self.pad}// try-else (no exception path):")
            lines.extend(self.gen_block(node.else_body))
        
        return lines

    _IMPORT_MAP = {
    "os": "import path from 'path';\nimport fs from 'fs';",
    "math": "const math = Math;",
    "json": "const json = JSON;",
    "random": "const random = { random: () => Math.random(), randint: (a,b) => Math.floor(Math.random() * (b - a + 1)) + a, choice: (arr) => arr[Math.floor(Math.random() * arr.length)] };",
    "sys": "const sys = { argv: process.argv, exit: (code = 0) => process.exit(code) };",
    "re": "const re = RegExp;",
    "time": "const time = { time: () => Date.now() / 1000 };",
    "datetime": "const datetime = Date;",
    "collections": "",
    "itertools": "",
    "functools": "",
    "pathlib": "import path from 'path';",
    "copy": "const copy = { copy: (x) => Array.isArray(x) ? [...x] : {...x}, deepcopy: (x) => JSON.parse(JSON.stringify(x)) };",
    "io": "import fs from 'fs';",
    "typing": "",
    "abc": "",
    "secrets": "const secrets = { randbelow: (n) => Math.floor(Math.random() * n) };"
}

    def gen_import(self, node):
        lines = []
        for mod, import_alias in node.names:
            base = mod.split(".")[0]
            if base in self._IMPORT_MAP:
                mapped = self._IMPORT_MAP[base]
                if import_alias and not mapped.startswith("//"):
                    lines.append(f"{self.pad}{mapped}  // as {import_alias}")
                else:
                    for ln in mapped.split("\n"):
                        lines.append(f"{self.pad}{ln}")
            else:
                alias_str = f" as {import_alias}" if import_alias else ""
                name      = import_alias if import_alias else base
                lines.append(f"{self.pad}import {name} from '{mod}';  // {mod}{alias_str}")
        return lines

    _FROM_IMPORT_MAP = {
        "flask":        "import express from 'express';\nconst { Router } = express;  // Flask → express",
        "django":       "// django → no direct Node.js equivalent; consider Express",
        "fastapi":      "import express from 'express';  // fastapi → express",
        "sqlalchemy":   "// sqlalchemy → consider using 'sequelize' or 'knex' in Node.js",
        "pydantic":     "// pydantic → consider using 'zod' or 'joi' for validation",
        "typing":       "// typing → not needed in JavaScript",
        "abc":          "// abc → not needed in JavaScript",
        "dataclasses":  "// dataclasses → use plain classes in JavaScript",
        "pathlib":      "import path from 'path';  // pathlib → path",
        "os.path":      "import path from 'path';",
        "collections":  "// collections → use Map/Set/Array in JavaScript",
        "functools":    "// functools → use Array/Function methods",
        "itertools":    "// itertools → use Array methods",
        "copy":         "// copy → use spread operator",
        "json":         "// json → JSON is a global in JavaScript",
        "math":         "// math → use Math (global)",
        "re":           "// re → use RegExp in JavaScript",
        "sys":          "// sys → not needed in Node.js",
        "io":           "// io → use Node.js 'fs' streams",
    }
    
    def gen_from_import(self, node):
        mod = node.module
        if mod in self._FROM_IMPORT_MAP:
            lines = []
            for ln in self._FROM_IMPORT_MAP[mod].split("\n"):
                lines.append(f"{self.pad}{ln}")
            return lines
        
        names_js = ", ".join(
            (f"{n} as {a}" if a else n) for n, a in node.names if n != "*"
        )
        
        if any(n == "*" for n, _ in node.names):
            return [f"{self.pad}import * as {mod.split('.')[-1]} from '{mod}';"]
        return [f"{self.pad}import {{ {names_js} }} from '{mod}';"]

    def gen_block(self, stmts):
        self.indent()
        lines = []
        for stmt in stmts:
            lines.extend(self.gen_stmt(stmt))
        self.dedent()
        return lines

    def gen_expr(self, node):
        if isinstance(node, Number):          
            return self.gen_number(node)
        if isinstance(node, String):          
            return self.gen_string(node)
        if isinstance(node, FString):         
            return self.gen_fstring(node)
        if isinstance(node, BoolLiteral):     
            return "true" if node.value else "false"
        if isinstance(node, NoneLiteral):     
            return "null"
        if isinstance(node, Identifier):      
            return self._map_identifier(node.name)
        if isinstance(node, Attribute):       
            return self.gen_attribute(node)
        if isinstance(node, Subscript):       
            return self.gen_subscript(node)
        if isinstance(node, Slice):           
            return self.gen_slice(node)
        if isinstance(node, BinaryOp):        
            return self.gen_binary(node)
        if isinstance(node, UnaryOp):         
            return self.gen_unary(node)
        if isinstance(node, BoolOp):          
            return self.gen_boolop(node)
        if isinstance(node, Ternary):         
            return self.gen_ternary(node)
        if isinstance(node, Lambda):          
            return self.gen_lambda(node)
        if isinstance(node, FunctionCall):    
            return self.gen_call(node)
        if isinstance(node, MethodCall):      
            return self.gen_method_call(node)
        if isinstance(node, ListLiteral):     
            return self.gen_list(node)
        if isinstance(node, DictLiteral):     
            return self.gen_dict(node)
        if isinstance(node, TupleLiteral):    
            return self.gen_tuple(node)
        if isinstance(node, SetLiteral):      
            return self.gen_set(node)
        if isinstance(node, ListComp):        
            return self.gen_list_comp(node)
        raise CodeGenError(f"Unknown expression node: {type(node).__name__}")

    def gen_number(self, node):
        v = node.value
        low = v.lower()
        if low.startswith("0x") or low.startswith("0b") or low.startswith("0o"):
            return v
        if "e" in low:
            return v
        try:
            f = float(v)
            if f == int(f) and "." in v:
                return str(int(f))
        except (ValueError, OverflowError):
            pass
        return v

    def gen_string(self, node):
        """Generate string literal."""
        escaped = (node.value
                   .replace("\\", "\\\\")
                   .replace('"', '\\"')
                   .replace("\n", "\\n")
                   .replace("\r", "\\r")
                   .replace("\t", "\\t"))
        print(repr(node.value))
        return f'"{escaped}"'

    def gen_fstring(self, node):
        from lexer import Lexer as _Lexer
        from parser import Parser as _Parser
        
        content = node.value
        content = content.replace("\\n", "\n").replace("\\t", "\t")
        
        def _replace(m):
            raw = m.group(1).strip()
            fmt_spec = None
            
            if ":" in raw:
                expr_part, fmt_part = raw.rsplit(":", 1)
                fmt_match = re.match(r'^([<>^]?)(\d+)', fmt_part.strip())
                if fmt_match:
                    raw      = expr_part.strip()
                    align    = fmt_match.group(1) or "<"
                    width    = fmt_match.group(2)
                    fmt_spec = (align, width)
            
            try:
                tokens  = _Lexer(raw).tokenize()
                expr    = _Parser(tokens).expression()
                js_expr = self.gen_expr(expr)
                
                if fmt_spec:
                    align, width = fmt_spec
                    if align == "<":
                        js_expr = f"{js_expr}.padEnd({width})"
                    elif align == ">":
                        js_expr = f"{js_expr}.padStart({width})"
                    elif align == "^":
                        js_expr = (f"{js_expr}.padStart("
                                   f"Math.floor(({width} + {js_expr}.length) / 2))"
                                   f".padEnd({width})")
                
                return "${" + js_expr + "}"
            except Exception:
                return "${" + raw + "}"
        
        result = re.sub(r'\{([^{}]+)\}', _replace, content)
        result = result.replace("`", "\\`")
        return f'`{result}`'

    def _map_identifier(self, name):
        if name == "self":      
            return "this"
        if name == "True":      
            return "true"
        if name == "False":     
            return "false"
        if name == "None":      
            return "null"
        if name == "__file__":  
            return "__filename"
        if name == "__name__":  
            return "__name__"   
        return name

    def gen_attribute(self, node):
        obj = self.gen_expr(node.value)
        return f"{obj}.{node.attr}"

    def gen_subscript(self, node):
        obj = self.gen_expr(node.value)
        if isinstance(node.index, Slice):
            return self._gen_slice_call(obj, node.index)
        idx = self.gen_expr(node.index)
        return f"{obj}[{idx}]"

    def _gen_slice_call(self, obj, sl):
        lower = self.gen_expr(sl.lower) if sl.lower else "0"
        upper = self.gen_expr(sl.upper) if sl.upper else None
        step  = self.gen_expr(sl.step)  if sl.step  else None

        if step:
            ub = upper if upper else f"{obj}.length"
            return (f"Array.from({{length: Math.ceil(({ub} - {lower}) / {step})}}, "
                    f"(_, i) => {obj}[{lower} + i * {step}])")
        if upper:
            return f"{obj}.slice({lower}, {upper})"
        return f"{obj}.slice({lower})"

    def gen_slice(self, node):
        lower = self.gen_expr(node.lower) if node.lower else "0"
        upper = self.gen_expr(node.upper) if node.upper else ""
        return f"{lower}:{upper}"

    def gen_list(self, node):
        items = ", ".join(self.gen_expr(e) for e in node.elements)
        return f"[{items}]"

    def gen_dict(self, node):
        pairs = ", ".join(
            f"{self.gen_expr(k)}: {self.gen_expr(v)}"
            for k, v in node.pairs
        )
        return "{" + pairs + "}"

    def gen_tuple(self, node):
        items = ", ".join(self.gen_expr(e) for e in node.elements)
        return f"[{items}]"

    def gen_set(self, node):
        items = ", ".join(self.gen_expr(e) for e in node.elements)
        return f"new Set([{items}])"

    def gen_list_comp(self, node):
        iter_js = self.gen_expr(node.iter_)
        elt_js  = self.gen_expr(node.elt)
        var     = node.target
        
        if node.cond:
            cond_js = self.gen_expr(node.cond)
            return f"{iter_js}.filter(({var}) => {cond_js}).map(({var}) => {elt_js})"
        return f"{iter_js}.map(({var}) => {elt_js})"

    def gen_binary(self, node):
        left  = self.gen_expr(node.left)
        right = self.gen_expr(node.right)

        if node.op.name == "FLOOR_DIVIDE":
            return f"Math.floor({left} / {right})"
        
        if node.op.name == "MULTIPLY":
            if isinstance(node.left, String):
                return f"{left}.repeat({right})"
            if isinstance(node.right, String):
                return f"{right}.repeat({left})"
        
        if node.op.name == "IN":
            if isinstance(node.right, (ListLiteral, TupleLiteral)):
                return f"{right}.includes({left})"
            return f"(Array.isArray({right}) ? {right}.includes({left}) : ({left} in {right}))"
        
        if node.op.name == "NOT_IN":
            if isinstance(node.right, (ListLiteral, TupleLiteral)):
                return f"!{right}.includes({left})"
            return f"!(Array.isArray({right}) ? {right}.includes({left}) : ({left} in {right}))"
        
        if node.op.name == "POWER":
            if isinstance(node.right, Number):
                return f"{self._maybe_paren(node.left, left)} ** {right}"
            return f"Math.pow({left}, {right})"

        js_op = _OP_MAP.get(node.op.name)
        if js_op is None:
            raise CodeGenError(f"Unsupported operator: {node.op.name}")

        left  = self._maybe_paren(node.left, left)
        right = self._maybe_paren(node.right, right)
        return f"{left} {js_op} {right}"

    def _maybe_paren(self, child_node, child_js):
        if isinstance(child_node, BinaryOp):
            return f"({child_js})"
        if isinstance(child_node, BoolOp):
            return f"({child_js})"
        return child_js

    def gen_unary(self, node):
        if node.op == "not" and isinstance(node.operand, BinaryOp) and node.operand.op.name == "IN":
            left  = self.gen_expr(node.operand.left)
            right = self.gen_expr(node.operand.right)
            if isinstance(node.operand.right, (ListLiteral, TupleLiteral)):
                return f"!{right}.includes({left})"
            return f"!(Array.isArray({right}) ? {right}.includes({left}) : ({left} in {right}))"
        
        operand = self.gen_expr(node.operand)
        if node.op == "not":
            return f"!({operand})"
        if node.op == "-":
            return f"-{operand}"
        if node.op == "~":
            return f"~{operand}"
        if node.op == "*spread*":
            return f"...{operand}"
        return f"{node.op}{operand}"

    def gen_boolop(self, node):
        js_op  = "&&" if node.op == "and" else "||"
        parts  = [f"({self.gen_expr(v)})" if isinstance(v, BoolOp) else self.gen_expr(v)
                  for v in node.values]
        return f" {js_op} ".join(parts)

    def gen_ternary(self, node):
        test   = self.gen_expr(node.test)
        body   = self.gen_expr(node.body)
        orelse = self.gen_expr(node.orelse)
        return f"({test} ? {body} : {orelse})"

    def gen_lambda(self, node):
        params = ", ".join(node.params)
        body   = self.gen_expr(node.body)
        return f"(({params}) => {body})"

    def gen_call(self, node):
        name = node.name
        args = node.args
        js_args = [self.gen_expr(a) for a in args]
        kw_args = {k: self.gen_expr(v) for k, v in node.kwargs.items()}

        if name == "len" and len(args) == 1:
            return f"{js_args[0]}.length"

        if name == "int":
            if len(args) == 1:
                return f"parseInt({js_args[0]})"
            if len(args) == 2:
                return f"parseInt({js_args[0]}, {js_args[1]})"

        if name == "range":
            if len(args) == 1:
                return f"Array.from({{length: {js_args[0]}}}, (_, i) => i)"
            if len(args) == 2:
                return (f"Array.from({{length: Math.max(0, {js_args[1]} - {js_args[0]})}}, "
                        f"(_, i) => i + {js_args[0]})")
            if len(args) == 3:
                step = js_args[2]
                return (f"Array.from({{length: Math.max(0, Math.ceil(({js_args[1]} - {js_args[0]}) / {step}))}}, "
                        f"(_, i) => {js_args[0]} + i * {step})")
            return f"/* range({', '.join(js_args)}) */"

        if name == "sorted":
            if len(args) == 1:
                return f"[...{js_args[0]}].sort()"
            if "key" in kw_args:
                return f"[...{js_args[0]}].sort((a, b) => {kw_args['key']}(a) > {kw_args['key']}(b) ? 1 : -1)"
            return f"[...{js_args[0]}].sort()"

        if name == "reversed":
            return f"[...{js_args[0]}].reverse()" if js_args else "[]"

        if name == "sum":
            if js_args:
                initial = js_args[1] if len(js_args) > 1 else "0"
                return f"{js_args[0]}.reduce((a, b) => a + b, {initial})"
            return "0"

        if name == "any":
            return f"{js_args[0]}.some(Boolean)" if js_args else "false"

        if name == "all":
            return f"{js_args[0]}.every(Boolean)" if js_args else "true"

        if name == "enumerate":
            src = js_args[0]
            return f"{src}.map((v, i) => [i, v])"

        if name == "zip":
            if len(js_args) == 0:
                return "[]"
            if len(js_args) == 1:
                return f"{js_args[0]}.map(v => [v])"
            if len(js_args) == 2:
                return f"{js_args[0]}.map((v, i) => [v, {js_args[1]}[i]])"
            arr_list = ", ".join(js_args)
            return (f"Array.from({{length: Math.min(...[{arr_list}].map(a => a.length))}}, "
                    f"(_, i) => [{arr_list}].map(a => a[i]))")

        if name == "map":
            if len(args) == 2:
                return f"{js_args[1]}.map({js_args[0]})"
            return f"/* map({', '.join(js_args)}) */"

        if name == "filter":
            if len(args) == 2:
                return f"{js_args[1]}.filter({js_args[0]})"
            return f"/* filter({', '.join(js_args)}) */"

        if name == "isinstance":
            if len(args) == 2:
                cls_name = args[1].name if isinstance(args[1], Identifier) else ""
                cls_js = _BUILTIN_MAP.get(cls_name, js_args[1])
                return f"({js_args[0]} instanceof {cls_js})"
            return f"/* isinstance */"
        
        if name == "hasattr":
            if len(args) == 2:
                return f"({js_args[1]} in {js_args[0]})"
            return "/* hasattr */"

        if name == "getattr":
            if len(args) == 2:
                return f"{js_args[0]}[{js_args[1]}]"
            if len(args) == 3:
                return f"({js_args[0]}[{js_args[1]}] !== undefined ? {js_args[0]}[{js_args[1]}] : {js_args[2]})"
            return "/* getattr */"

        if name == "setattr":
            if len(args) == 3:
                return f"{js_args[0]}[{js_args[1]}] = {js_args[2]}"
            return "/* setattr */"

        if name == "dict":
            if not args:
                return "{}"
            return f"Object.fromEntries({js_args[0]})"

        if name == "set":
            items = ", ".join(js_args)
            return f"new Set([{items}])"

        if name == "repr":
            return f"JSON.stringify({js_args[0]})" if js_args else '""'

        if name == "ord":
            return f"{js_args[0]}.charCodeAt(0)" if js_args else "0"

        if name == "hex":
            return f"'0x' + {js_args[0]}.toString(16)" if js_args else '"0x0"'

        if name == "oct":
            return f"'0o' + {js_args[0]}.toString(8)" if js_args else '"0o0"'

        if name == "bin":
            return f"'0b' + {js_args[0]}.toString(2)" if js_args else '"0b0"'

        if name == "abs":
            return f"Math.abs({js_args[0]})" if js_args else "0"

        if name == "super":
            return "super"

        if name == "Flask":
            return "express()"

        if name == "jsonify":
            return f"/* jsonify → */ ({', '.join(js_args)})"
        
        exc_names = {
            "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
            "AttributeError", "NameError", "RuntimeError", "NotImplementedError",
            "AssertionError", "ZeroDivisionError", "StopIteration",
            "OSError", "IOError", "FileNotFoundError",
        }
        if name in exc_names:
            js_cls = _BUILTIN_MAP.get(name, "Error")
            return f"new {js_cls}({', '.join(js_args)})"
        
        js_name = _BUILTIN_MAP.get(name)
        if js_name is not None:
            all_args = js_args[:]
            if kw_args:
                kw_obj = "{" + ", ".join(f"{k}: {v}" for k, v in kw_args.items()) + "}"
                all_args.append(kw_obj)
            return f"{js_name}({', '.join(all_args)})"
        
        all_args = js_args[:]
        if kw_args:
            kw_obj = "{" + ", ".join(f"{k}: {v}" for k, v in kw_args.items()) + "}"
            all_args.append(kw_obj)
        
        if name in self._class_names:
            return f"new {name}({', '.join(all_args)})"
        
        return f"{name}({', '.join(all_args)})"

    def gen_method_call(self, node):
        obj    = self.gen_expr(node.obj)
        method = node.method
        args   = [self.gen_expr(a) for a in node.args]
        kwargs = {k: self.gen_expr(v) for k, v in node.kwargs.items()}
        
        if (isinstance(node.obj, Attribute) and
                isinstance(node.obj.value, Identifier) and
                node.obj.value.name == "os" and node.obj.attr == "path"):
            if method == "join":
                return f"path.join({', '.join(args)})"
            if method == "dirname":
                return f"path.dirname({', '.join(args)})"
            if method == "abspath":
                return f"path.resolve({', '.join(args)})"
            if method == "basename":
                return f"path.basename({', '.join(args)})"
            if method == "exists":
                return f"fs.existsSync({', '.join(args)})"
            if method == "splitext":
                return f"path.parse({', '.join(args)})"
            if method == "isfile":
                return f"fs.statSync({', '.join(args)}).isFile()"
            if method == "isdir":
                return f"fs.statSync({', '.join(args)}).isDirectory()"
            return f"path.{method}({', '.join(args)})"
        
        if (isinstance(node.obj, Attribute) and
                isinstance(node.obj.value, Identifier) and
                node.obj.value.name == "sys" and node.obj.attr == "path"):
            return f"/* sys.path.{method}({', '.join(args)}) — not needed in Node.js */"
        
        if method == "run" and not args:
            port = kwargs.get("port", '"3000"')
            return f"{obj}.listen({port})"
        
        if (isinstance(node.obj, FunctionCall) and
                node.obj.name == "super" and method == "__init__"):
            return f"super({', '.join(args)})"
        
        if isinstance(node.obj, FunctionCall) and node.obj.name == "super":
            return f"super.{method}({', '.join(args)})"
        
        if method == "append":
            return f"{obj}.push({', '.join(args)})"
        
        if method == "extend":
            return f"{obj}.push(...{args[0]})" if args else f"{obj}.push()"
        
        if method == "insert":
            if len(args) == 2:
                return f"{obj}.splice({args[0]}, 0, {args[1]})"
        
        if method == "remove":
            return f"{obj}.splice({obj}.indexOf({args[0]}), 1)" if args else f"{obj}.splice(0, 1)"
        
        if method == "pop":
            if args:
                arg = args[0]
                is_dict_pop = (arg.startswith('"') or arg.startswith("'") or
                               not arg.lstrip('-').isdigit())
                if is_dict_pop:
                    return (f"((_v = {obj}[{arg}]), delete {obj}[{arg}], _v)")
                return f"{obj}.splice({arg}, 1)[0]"
            return f"{obj}.pop()"
        
        if method == "index":
            return f"{obj}.indexOf({', '.join(args)})"
        
        if method == "count":
            return f"{obj}.filter(x => x === {args[0]}).length" if args else f"{obj}.length"
        
        if method == "copy":
            return f"[...{obj}]"
        
        if method == "clear":
            return f"({obj}.length = 0, undefined)"
        
        if method == "keys":
            return f"Object.keys({obj})"
        
        if method == "values":
            return f"Object.values({obj})"
        
        if method == "items":
            return f"Object.entries({obj})"
        
        if method == "get":
            if len(args) == 1:
                return f"({obj}[{args[0]}] !== undefined ? {obj}[{args[0]}] : null)"
            if len(args) == 2:
                return f"({obj}[{args[0]}] !== undefined ? {obj}[{args[0]}] : {args[1]})"
        
        if method == "update":
            return f"Object.assign({obj}, {args[0]})" if args else f"{obj}"
        
        if method == "join":
            return f"{args[0]}.join({obj})" if args else f"{obj}.join('')"
        
        if method == "format":
            if args:
                return f"`{obj.strip('\"')}`.replace(/{{0}}/g, {args[0]})"
            return f"`{obj.strip('\"')}`"
        
        if method == "encode":
    
            encoding = args[0].strip('"\'') if args else "utf-8"
            return f"Buffer.from({obj}, '{encoding}')"
        
        if method == "decode":
            encoding = args[0].strip('"\'') if args else "utf-8"
            return f"{obj}.toString('{encoding}')"
        
        if method == "isdigit":
            return f"/^\\d+$/.test({obj})"
        
        if method == "isalpha":
            return f"/^[a-zA-Z]+$/.test({obj})"
        
        if method == "isalnum":
            return f"/^[a-zA-Z0-9]+$/.test({obj})"
        
        if method == "zfill":
            return f"{obj}.padStart({args[0]}, '0')" if args else obj
        
        if method == "center":
            return f"{obj}.padStart(Math.floor(({args[0]} + {obj}.length) / 2)).padEnd({args[0]})" if args else obj
        
        if method == "strip":
            return f"{obj}.trim()"
        
        if method == "lstrip":
            return f"{obj}.trimStart()"
        
        if method == "rstrip":
            return f"{obj}.trimEnd()"
        
        if method == "upper":
            return f"{obj}.toUpperCase()"
        
        if method == "lower":
            return f"{obj}.toLowerCase()"
        
        if method == "startswith":
            return f"{obj}.startsWith({', '.join(args)})"
        
        if method == "endswith":
            return f"{obj}.endsWith({', '.join(args)})"
        
        if method == "find":
            return f"{obj}.indexOf({', '.join(args)})"
        
        if method == "rfind":
            return f"{obj}.lastIndexOf({', '.join(args)})"
        
        if method == "replace":
            if len(args) == 2:
                return f"{obj}.split({args[0]}).join({args[1]})"
            return f"{obj}.replace({', '.join(args)})"
        
        if method == "split":
            return f"{obj}.split({', '.join(args)})"
        
        if method == "sort":
            if "key" in kwargs:
                return f"{obj}.sort((a, b) => {kwargs['key']}(a) > {kwargs['key']}(b) ? 1 : -1)"
            reverse = kwargs.get("reverse", "")
            if reverse == "true":
                return f"{obj}.sort().reverse()"
            return f"{obj}.sort()"
        
        if method == "reverse":
            return f"{obj}.reverse()"

        if method == "add":
            return f"{obj}.add({', '.join(args)})"
        
        if method == "discard":
            return f"{obj}.delete({', '.join(args)})"
        
        if method == "has":
            return f"{obj}.has({', '.join(args)})"
        
        all_args = args + [f"{k}={v}" for k, v in kwargs.items()]
        return f"{obj}.{method}({', '.join(all_args)})"
