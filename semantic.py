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
from lexer import Lexer
from parser import Parser

class SemanticError(Exception):
    pass


class Scope:
    def __init__(self, parent=None, name="<module>"):
        self.symbols = {}
        self.parent  = parent
        self.name    = name

    def define(self, name, kind="variable"):
        self.symbols[name] = kind

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def defined_locally(self, name):
        return name in self.symbols

_BUILTINS = {
    "print", "len", "range", "int", "float", "str", "bool", "list",
    "dict", "set", "tuple", "type", "isinstance", "issubclass",
    "hasattr", "getattr", "setattr", "delattr", "callable",
    "input", "abs", "max", "min", "sum", "round", "pow", "divmod",
    "sorted", "reversed", "enumerate", "zip", "map", "filter",
    "any", "all", "next", "iter", "id", "hash",
    "open", "repr", "hex", "oct", "bin", "chr", "ord",
    "vars", "dir", "globals", "locals", "eval", "exec",
    "staticmethod", "classmethod", "property",
    "super", "object",
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "AttributeError", "NameError", "RuntimeError", "StopIteration",
    "OSError", "IOError", "FileNotFoundError", "PermissionError",
    "ZeroDivisionError", "OverflowError", "MemoryError",
    "NotImplementedError", "AssertionError",
    "True", "False", "None",
    "word", "largest", "least", "sqrt",  
}


class SemanticAnalyzer:
    def __init__(self):
        self.scope        = Scope(name="<module>")
        self._in_function = False
        self._in_class    = False
        self._in_loop     = False
        self._globals     = set()

    def _push_scope(self, name="<block>"):
        self.scope = Scope(parent=self.scope, name=name)

    def _pop_scope(self):
        self.scope = self.scope.parent

    def _define(self, name):
        self.scope.define(name)

    def _check_name(self, name, node_desc="variable"):
        if name in _BUILTINS:
            return
        if self.scope.lookup(name) is None and name not in self._globals:
            raise SemanticError(
                f"Name '{name}' used before assignment ({node_desc})"
            )

    def analyze(self, node):
        method = getattr(self, f"_visit_{type(node).__name__}", self._visit_generic)
        return method(node)

    def _visit_generic(self, node):
        pass  

    def _visit_Program(self, node):
        for stmt in node.statements:
            self.analyze(stmt)

    def _visit_FunctionDef(self, node):
        self._define(node.name)
        saved_fn    = self._in_function
        self._in_function = True
        self._push_scope(f"fn:{node.name}")
        for p in node.params:
            self._define(p)
        if node.vararg:
            self._define(node.vararg)
        if node.kwarg:
            self._define(node.kwarg)
        self._pop_scope()
        for default in node.defaults.values():
            self.analyze(default)
        self._push_scope(f"fn:{node.name}")
        for p in node.params:
            self._define(p)
        if node.vararg:
            self._define(node.vararg)
        if node.kwarg:
            self._define(node.kwarg)
        for stmt in node.body:
            self.analyze(stmt)
        self._pop_scope()
        self._in_function = saved_fn

    def _visit_ClassDef(self, node):
        self._define(node.name)
        saved_cls   = self._in_class
        self._in_class = True
        self._push_scope(f"class:{node.name}")
        self._define("self")
        for stmt in node.body:
            self.analyze(stmt)
        self._pop_scope()
        self._in_class = saved_cls

    def _visit_Assignment(self, node):
        self.analyze(node.value)
        self._define(node.name)

    def _visit_ComplexAssignment(self, node):
        self.analyze(node.target)
        self.analyze(node.value)

    def _visit_AugmentedAssignment(self, node):
        self.analyze(node.target)
        self.analyze(node.value)

    def _visit_Print(self, node):
        self.analyze(node.expression)

    def _visit_Return(self, node):
        if not self._in_function:
            raise SemanticError("'return' outside function")
        if node.value:
            self.analyze(node.value)

    def _visit_Raise(self, node):
        if node.exc:
            self.analyze(node.exc)

    def _visit_Delete(self, node):
        for t in node.targets:
            self.analyze(t)

    def _visit_Assert(self, node):
        self.analyze(node.test)
        if node.msg:
            self.analyze(node.msg)

    def _visit_Pass(self, node):   pass
    def _visit_Break(self, node):  pass
    def _visit_Continue(self, node): pass

    def _visit_Global(self, node):
        for n in node.names:
            self._globals.add(n)

    def _visit_Nonlocal(self, node):
        pass   

    def _visit_If(self, node):
        self.analyze(node.condition)
        for s in node.body:        self.analyze(s)
        for cond, body in node.elif_clauses:
            self.analyze(cond)
            for s in body: self.analyze(s)
        for s in node.else_body:   self.analyze(s)

    def _visit_While(self, node):
        self.analyze(node.condition)
        saved = self._in_loop;  self._in_loop = True
        for s in node.body:    self.analyze(s)
        self._in_loop = saved

    def _visit_For(self, node):
        self.analyze(node.start)
        self.analyze(node.stop)
        if node.step:    self.analyze(node.step)
        self._define(node.var)
        saved = self._in_loop;  self._in_loop = True
        for s in node.body:    self.analyze(s)
        self._in_loop = saved

    def _visit_ForIn(self, node):
        self.analyze(node.iterable)
        if isinstance(node.var, list):
            for v in node.var:
                self._define(v)
        else:
            self._define(node.var)
        saved = self._in_loop;  self._in_loop = True
        for s in node.body:    self.analyze(s)
        self._in_loop = saved

    def _visit_With(self, node):
        self.analyze(node.expr)
        if node.alias:
            self._define(node.alias)
        for s in node.body:    self.analyze(s)

    def _visit_TryExcept(self, node):
        for s in node.body:        self.analyze(s)
        for h in node.handlers:
            if h.name:
                self._define(h.name)
            for s in h.body:       self.analyze(s)
        for s in node.else_body:   self.analyze(s)
        for s in node.final_body:  self.analyze(s)


    def _visit_Import(self, node):
        for mod, alias in node.names:
            self._define(alias if alias else mod.split(".")[0])

    def _visit_FromImport(self, node):
        for name, alias in node.names:
            if name != "*":
                self._define(alias if alias else name)


    def _visit_BinaryOp(self, node):
        self.analyze(node.left)
        self.analyze(node.right)

    def _visit_UnaryOp(self, node):
        self.analyze(node.operand)

    def _visit_BoolOp(self, node):
        for v in node.values:
            self.analyze(v)

    def _visit_Ternary(self, node):
        self.analyze(node.test)
        self.analyze(node.body)
        self.analyze(node.orelse)

    def _visit_Lambda(self, node):
        self._push_scope("lambda")
        for p in node.params:
            self._define(p)
        self.analyze(node.body)
        self._pop_scope()

    def _visit_FunctionCall(self, node):
        for a in node.args:    self.analyze(a)
        for v in node.kwargs.values(): self.analyze(v)

    def _visit_MethodCall(self, node):
        self.analyze(node.obj)
        for a in node.args:    self.analyze(a)
        for v in node.kwargs.values(): self.analyze(v)

    def _visit_Attribute(self, node):
        self.analyze(node.value)

    def _visit_Subscript(self, node):
        self.analyze(node.value)
        self.analyze(node.index)

    def _visit_Slice(self, node):
        if node.lower:  self.analyze(node.lower)
        if node.upper:  self.analyze(node.upper)
        if node.step:   self.analyze(node.step)

    def _visit_ListLiteral(self, node):
        for e in node.elements: self.analyze(e)

    def _visit_DictLiteral(self, node):
        for k, v in node.pairs:
            self.analyze(k);  self.analyze(v)

    def _visit_TupleLiteral(self, node):
        for e in node.elements: self.analyze(e)

    def _visit_SetLiteral(self, node):
        for e in node.elements: self.analyze(e)

    def _visit_ListComp(self, node):
        self._push_scope("listcomp")
        self._define(node.target)
        self.analyze(node.iter_)
        if node.cond:  self.analyze(node.cond)
        self.analyze(node.elt)
        self._pop_scope()

    def _visit_Identifier(self, node):
        pass
    
    def _visit_Number(self, n):      pass
    def _visit_String(self, n):      pass
    def _visit_FString(self, n):     pass
    def _visit_BoolLiteral(self, n): pass
    def _visit_NoneLiteral(self, n): pass



def main():
    print("Enter your program (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "": break
        lines.append(line)
    source = "\n".join(lines)
    try:
        ast = Parser(Lexer(source).tokenize()).parse()
        SemanticAnalyzer().analyze(ast)
        print("Semantic analysis completed successfully!")
    except SemanticError as e:
        print("Semantic Error:", e)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()