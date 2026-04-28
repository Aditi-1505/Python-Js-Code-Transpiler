from parser import (
    Parser, Program,
    Number, String, FString, BoolLiteral, NoneLiteral,
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
from lexer import Lexer

class SymbolTableGenerator:

    def __init__(self):
        self.symbol_table = {}

    def generate(self, node):
        self._visit(node)
        return self.symbol_table

    def _visit(self, node):
        if node is None:
            return
        name   = type(node).__name__
        method = getattr(self, f"_v_{name}", self._v_generic)
        method(node)

    def _visit_all(self, nodes):
        for n in (nodes or []):
            self._visit(n)

    def _v_generic(self, node):
        pass  


    def _v_Program(self, node):
        self._visit_all(node.statements)


    def _v_FunctionDef(self, node):
        self.symbol_table[node.name] = "function"
        for p in node.params:
            self.symbol_table[p] = "parameter"
        if node.vararg:
            self.symbol_table[node.vararg] = "parameter"
        if node.kwarg:
            self.symbol_table[node.kwarg] = "parameter"
        for default in node.defaults.values():
            self._visit(default)
        self._visit_all(node.body)

    def _v_ClassDef(self, node):
        self.symbol_table[node.name] = "class"
        self._visit_all(node.body)

    def _v_Assignment(self, node):
        self.symbol_table[node.name] = "variable"
        self._visit(node.value)

    def _v_ComplexAssignment(self, node):
        self._visit(node.target)
        self._visit(node.value)

    def _v_AugmentedAssignment(self, node):
        self._visit(node.target)
        self._visit(node.value)

    def _v_Print(self, node):       self._visit(node.expression)
    def _v_Return(self, node):
        if node.value: self._visit(node.value)
    def _v_Raise(self, node):
        if node.exc:   self._visit(node.exc)
    def _v_Delete(self, node):      self._visit_all(node.targets)
    def _v_Assert(self, node):
        self._visit(node.test)
        if node.msg: self._visit(node.msg)
    def _v_Pass(self, node):        pass
    def _v_Break(self, node):       pass
    def _v_Continue(self, node):    pass

    def _v_Global(self, node):
        for n in node.names:
            self.symbol_table[n] = "variable"

    def _v_Nonlocal(self, node):
        for n in node.names:
            if n not in self.symbol_table:
                self.symbol_table[n] = "variable"

    def _v_Import(self, node):
        for mod, alias in node.names:
            key = alias if alias else mod.split(".")[0]
            self.symbol_table[key] = "import"

    def _v_FromImport(self, node):
        for name, alias in node.names:
            if name == "*":
                self.symbol_table[f"{node.module}.*"] = "import"
            else:
                key = alias if alias else name
                self.symbol_table[key] = "import"

    def _v_If(self, node):
        self._visit(node.condition)
        self._visit_all(node.body)
        for cond, body in node.elif_clauses:
            self._visit(cond)
            self._visit_all(body)
        self._visit_all(node.else_body)

    def _v_While(self, node):
        self._visit(node.condition)
        self._visit_all(node.body)

    def _v_For(self, node):
        self.symbol_table[node.var] = "variable"
        self._visit(node.start)
        self._visit(node.stop)
        if node.step: self._visit(node.step)
        self._visit_all(node.body)

    def _v_ForIn(self, node):
        if isinstance(node.var, list):
            for v in node.var:
                self.symbol_table[v] = "variable"
        else:
            self.symbol_table[node.var] = "variable"
        self._visit(node.iterable)
        self._visit_all(node.body)

    def _v_With(self, node):
        self._visit(node.expr)
        if node.alias:
            self.symbol_table[node.alias] = "variable"
        self._visit_all(node.body)

    def _v_TryExcept(self, node):
        self._visit_all(node.body)
        for h in node.handlers:
            if h.name:
                self.symbol_table[h.name] = "variable"
            self._visit_all(h.body)
        self._visit_all(node.else_body)
        self._visit_all(node.final_body)

    def _v_BinaryOp(self, node):
        self._visit(node.left)
        self._visit(node.right)

    def _v_UnaryOp(self, node):     self._visit(node.operand)
    def _v_BoolOp(self, node):      self._visit_all(node.values)
    def _v_Ternary(self, node):
        self._visit(node.test)
        self._visit(node.body)
        self._visit(node.orelse)

    def _v_Lambda(self, node):
        for p in node.params:
            self.symbol_table[p] = "parameter"
        self._visit(node.body)

    def _v_FunctionCall(self, node):
        self.symbol_table[node.name] = "builtin" if _is_builtin(node.name) else "function"
        self._visit_all(node.args)
        for v in node.kwargs.values():
            self._visit(v)

    def _v_MethodCall(self, node):
        self._visit(node.obj)
        self._visit_all(node.args)
        for v in node.kwargs.values():
            self._visit(v)

    def _v_Attribute(self, node):   self._visit(node.value)
    def _v_Subscript(self, node):
        self._visit(node.value)
        self._visit(node.index)
    def _v_Slice(self, node):
        if node.lower: self._visit(node.lower)
        if node.upper: self._visit(node.upper)
        if node.step:  self._visit(node.step)

    def _v_ListLiteral(self, node):  self._visit_all(node.elements)
    def _v_DictLiteral(self, node):
        for k, v in node.pairs:
            self._visit(k); self._visit(v)
    def _v_TupleLiteral(self, node): self._visit_all(node.elements)
    def _v_SetLiteral(self, node):   self._visit_all(node.elements)

    def _v_ListComp(self, node):
        self.symbol_table[node.target] = "variable"
        self._visit(node.iter_)
        if node.cond: self._visit(node.cond)
        self._visit(node.elt)

    def _v_Identifier(self, node):
        if node.name not in self.symbol_table:
            self.symbol_table[node.name] = "variable"

    def _v_Number(self, n):      pass
    def _v_String(self, n):      pass
    def _v_FString(self, n):     pass
    def _v_BoolLiteral(self, n): pass
    def _v_NoneLiteral(self, n): pass

_KNOWN_BUILTINS = {
    "print", "len", "range", "int", "float", "str", "bool", "list",
    "dict", "set", "tuple", "type", "isinstance", "issubclass",
    "hasattr", "getattr", "setattr", "input", "abs", "max", "min",
    "sum", "round", "pow", "sorted", "reversed", "enumerate", "zip",
    "map", "filter", "any", "all", "next", "iter", "repr", "id",
    "hex", "oct", "bin", "chr", "ord", "open", "super",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
}

def _is_builtin(name):
    return name in _KNOWN_BUILTINS

def print_symbol_table(table):
    print("\nSYMBOL TABLE\n")
    print(f"{'NAME':<30} TYPE")
    print("-" * 40)
    order = ["function", "class", "variable", "parameter", "import", "builtin"]
    for kind in order:
        for name, typ in sorted(table.items()):
            if typ == kind:
                print(f"{name:<30} {typ}")
    for name, typ in sorted(table.items()):
        if typ not in order:
            print(f"{name:<30} {typ}")


# ── CLI ──────────────────────────────────────────────────────
def main():
    print("Enter your program (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "": break
        lines.append(line)
    source = "\n".join(lines)
    try:
        tokens    = Lexer(source).tokenize()
        ast       = Parser(tokens).parse()
        generator = SymbolTableGenerator()
        table     = generator.generate(ast)
        print_symbol_table(table)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()