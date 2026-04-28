from lexer import TokenType, Token, LexerError, Lexer

class ASTNode:
    pass
class Number(ASTNode):
    def __init__(self, value):      self.value = value
class String(ASTNode):
    def __init__(self, value):      self.value = value
class FString(ASTNode):
    def __init__(self, value):      self.value = value   
class BoolLiteral(ASTNode):
    def __init__(self, value):      self.value = value   
class NoneLiteral(ASTNode):
    pass
class ListLiteral(ASTNode):
    def __init__(self, elements):   self.elements = elements
class DictLiteral(ASTNode):
    def __init__(self, pairs):      self.pairs = pairs
class TupleLiteral(ASTNode):
    def __init__(self, elements):   self.elements = elements
class SetLiteral(ASTNode):
    def __init__(self, elements):   self.elements = elements
class Identifier(ASTNode):
    def __init__(self, name):       self.name = name
class Attribute(ASTNode):
    def __init__(self, value, attr):
        self.value = value;  self.attr = attr
class Subscript(ASTNode):
    def __init__(self, value, index):
        self.value = value;  self.index = index
class Slice(ASTNode):
    def __init__(self, lower, upper, step):
        self.lower = lower;  self.upper = upper;  self.step = step
class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left;  self.op = op;  self.right = right
class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op;  self.operand = operand
class BoolOp(ASTNode):
    def __init__(self, op, values):
        self.op = op;  self.values = values    
class Ternary(ASTNode):
    def __init__(self, body, test, orelse):
        self.body = body;  self.test = test;  self.orelse = orelse
class Lambda(ASTNode):
    def __init__(self, params, body):
        self.params = params;  self.body = body
class FunctionCall(ASTNode):
    def __init__(self, name, args, kwargs=None):
        self.name = name;  self.args = args;  self.kwargs = kwargs or {}
class MethodCall(ASTNode):
    def __init__(self, obj, method, args, kwargs=None):
        self.obj = obj;  self.method = method
        self.args = args;  self.kwargs = kwargs or {}
class ListComp(ASTNode):
    def __init__(self, elt, target, iter_, cond):
        self.elt = elt;  self.target = target
        self.iter_ = iter_;  self.cond = cond
class Program(ASTNode):
    def __init__(self, statements):  self.statements = statements
class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name;  self.value = value
class ComplexAssignment(ASTNode):
    def __init__(self, target, value):
        self.target = target;  self.value = value
class AugmentedAssignment(ASTNode):
    def __init__(self, target, op, value):
        self.target = target;  self.op = op;  self.value = value
class Print(ASTNode):
    def __init__(self, expression):  self.expression = expression
class Return(ASTNode):
    def __init__(self, value=None):  self.value = value
class Raise(ASTNode):
    def __init__(self, exc=None):    self.exc = exc
class Delete(ASTNode):
    def __init__(self, targets):     self.targets = targets
class Assert(ASTNode):
    def __init__(self, test, msg=None):
        self.test = test;  self.msg = msg
class Pass(ASTNode):       pass
class Break(ASTNode):      pass
class Continue(ASTNode):   pass
class Global(ASTNode):
    def __init__(self, names):   self.names = names
class Nonlocal(ASTNode):
    def __init__(self, names):   self.names = names
class If(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None):
        self.condition    = condition
        self.body         = body
        self.elif_clauses = elif_clauses or []
        self.else_body    = else_body or []
class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition;  self.body = body
class For(ASTNode):
    def __init__(self, var, start, stop, step, body):
        self.var = var;  self.start = start;  self.stop = stop
        self.step = step;  self.body = body
class ForIn(ASTNode):
    def __init__(self, var, iterable, body):
        # var is either a string (single target) or list of strings (tuple unpack)
        self.var = var;  self.iterable = iterable;  self.body = body
class With(ASTNode):
    def __init__(self, expr, alias, body):
        self.expr = expr;  self.alias = alias;  self.body = body
class FunctionDef(ASTNode):
    def __init__(self, name, params, body, defaults=None,
                 vararg=None, kwarg=None, decorators=None):
        self.name       = name
        self.params     = params        
        self.body       = body
        self.defaults   = defaults or {}  
        self.vararg     = vararg          
        self.kwarg      = kwarg           
        self.decorators = decorators or []
class ClassDef(ASTNode):
    def __init__(self, name, bases, body, decorators=None):
        self.name       = name
        self.bases      = bases          
        self.body       = body
        self.decorators = decorators or []
class TryExcept(ASTNode):
    def __init__(self, body, handlers, else_body, final_body):
        self.body       = body
        self.handlers   = handlers
        self.else_body  = else_body
        self.final_body = final_body
class ExceptHandler(ASTNode):
    def __init__(self, exc_type, name, body):
        self.exc_type = exc_type   
        self.name     = name       
        self.body     = body
class Import(ASTNode):
    def __init__(self, names):   self.names = names  
class FromImport(ASTNode):
    def __init__(self, module, names):
        self.module = module;  self.names = names      
class _Op:
    def __init__(self, token_type):
        self.name  = token_type.name
        self.value = token_type.value

class _Op_named:
    def __init__(self, name):
        self.name  = name
        self.value = name

_COMPARE_OPS = (
    TokenType.DOUBLE_EQUALS, TokenType.NOT_EQUALS,
    TokenType.LESS_THAN, TokenType.GREATER_THAN,
    TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL,
    TokenType.IN, TokenType.IS, TokenType.NOT,
)
_ADD_OPS = (TokenType.PLUS, TokenType.MINUS)
_MUL_OPS = (
    TokenType.MULTIPLY, TokenType.DIVIDE,
    TokenType.FLOOR_DIVIDE, TokenType.MODULO,
)
_AUG_OPS = {
    TokenType.PLUS_EQUALS, TokenType.MINUS_EQUALS,
    TokenType.MULTIPLY_EQUALS, TokenType.DIVIDE_EQUALS,
    TokenType.FLOOR_DIVIDE_EQUALS, TokenType.MODULO_EQUALS,
    TokenType.POWER_EQUALS,
}
_AUG_OP_STR = {
    TokenType.PLUS_EQUALS:         "+=",
    TokenType.MINUS_EQUALS:        "-=",
    TokenType.MULTIPLY_EQUALS:     "*=",
    TokenType.DIVIDE_EQUALS:       "/=",
    TokenType.FLOOR_DIVIDE_EQUALS: "//=",
    TokenType.MODULO_EQUALS:       "%=",
    TokenType.POWER_EQUALS:        "**=",
}

class Parser:
    def __init__(self, tokens):
        self.tokens   = tokens
        self.position = 0
        self.current  = self.tokens[0]

    def eat(self, token_type):
        if self.current.type == token_type:
            self.position += 1
            if self.position < len(self.tokens):
                self.current = self.tokens[self.position]
        else:
            raise SyntaxError(
                f"Expected {token_type.name}, "
                f"got {self.current.type.name} ({self.current.value!r}) "
                f"at line {self.current.line}"
            )

    def peek(self, offset=1):
        pos = self.position + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]

    def skip_newlines(self):
        while self.current.type in (TokenType.NEWLINE, TokenType.COMMENT):
            self.position += 1
            if self.position < len(self.tokens):
                self.current = self.tokens[self.position]

    def parse(self):
        statements = []
        while self.current.type != TokenType.EOF:
            self.skip_newlines()
            if self.current.type == TokenType.EOF:
                break
            statements.append(self.statement())
        return Program(statements)


    def statement(self):
        t = self.current

        if t.type == TokenType.AT:
            return self._parse_decorated()
        if t.type == TokenType.DEF:
            return self.function_def()
        if t.type == TokenType.CLASS:
            return self.class_def()
        if t.type == TokenType.IF:
            return self.if_statement()
        if t.type == TokenType.WHILE:
            return self.while_statement()
        if t.type == TokenType.FOR:
            return self.for_statement()
        if t.type == TokenType.TRY:
            return self.try_statement()
        if t.type == TokenType.WITH:
            return self.with_statement()
        if t.type == TokenType.RETURN:
            return self.return_stmt()
        if t.type == TokenType.RAISE:
            return self.raise_stmt()
        if t.type == TokenType.IMPORT:
            return self.import_stmt()
        if t.type == TokenType.FROM:
            return self.from_import_stmt()
        if t.type == TokenType.PASS:
            self.eat(TokenType.PASS);  return Pass()
        if t.type == TokenType.BREAK:
            self.eat(TokenType.BREAK); return Break()
        if t.type == TokenType.CONTINUE:
            self.eat(TokenType.CONTINUE); return Continue()
        if t.type == TokenType.GLOBAL:
            return self.global_stmt()
        if t.type == TokenType.NONLOCAL:
            return self.nonlocal_stmt()
        if t.type == TokenType.DEL:
            return self.del_stmt()
        if t.type == TokenType.ASSERT:
            return self.assert_stmt()
        if t.type == TokenType.PRINT:
            return self.print_statement()

        if t.type == TokenType.IDENTIFIER and self.peek().type == TokenType.EQUALS:
            return self.assignment()

        if t.type == TokenType.IDENTIFIER and self.peek().type in _AUG_OPS:
            name = t.value
            self.eat(TokenType.IDENTIFIER)
            op   = _AUG_OP_STR[self.current.type]
            self.eat(self.current.type)
            return AugmentedAssignment(Identifier(name), op, self.expression())

        expr = self.expression()

        if self.current.type in _AUG_OPS:
            op    = _AUG_OP_STR[self.current.type]
            self.eat(self.current.type)
            return AugmentedAssignment(expr, op, self.expression())

        if self.current.type == TokenType.EQUALS and isinstance(expr, (Attribute, Subscript)):
            self.eat(TokenType.EQUALS)
            return ComplexAssignment(expr, self.expression())

        return expr

    def assignment(self):
        name = self.current.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.EQUALS)
        return Assignment(name, self.expression())

    def print_statement(self):
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        args = []
        if self.current.type != TokenType.RPAREN:
            args.append(self.expression())
            while self.current.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expression())
        self.eat(TokenType.RPAREN)
        return Print(args[0]) if len(args) == 1 else FunctionCall("print", args)

    def return_stmt(self):
        self.eat(TokenType.RETURN)
        if self.current.type in (TokenType.NEWLINE, TokenType.EOF,
                                  TokenType.DEDENT, TokenType.COMMENT):
            return Return(None)
        return Return(self.expression())

    def raise_stmt(self):
        self.eat(TokenType.RAISE)
        if self.current.type in (TokenType.NEWLINE, TokenType.EOF,
                                  TokenType.DEDENT, TokenType.COMMENT):
            return Raise(None)
        return Raise(self.expression())

    def global_stmt(self):
        self.eat(TokenType.GLOBAL)
        names = [self.current.value]
        self.eat(TokenType.IDENTIFIER)
        while self.current.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            names.append(self.current.value)
            self.eat(TokenType.IDENTIFIER)
        return Global(names)

    def nonlocal_stmt(self):
        self.eat(TokenType.NONLOCAL)
        names = [self.current.value]
        self.eat(TokenType.IDENTIFIER)
        while self.current.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            names.append(self.current.value)
            self.eat(TokenType.IDENTIFIER)
        return Nonlocal(names)

    def del_stmt(self):
        self.eat(TokenType.DEL)
        targets = [self.expression()]
        while self.current.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            targets.append(self.expression())
        return Delete(targets)

    def assert_stmt(self):
        self.eat(TokenType.ASSERT)
        test = self.expression()
        msg  = None
        if self.current.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            msg = self.expression()
        return Assert(test, msg)

    def import_stmt(self):
        self.eat(TokenType.IMPORT)
        names = [self._read_dotted_name()]
        alias = None
        if self.current.type == TokenType.AS:
            self.eat(TokenType.AS)
            alias = self.current.value
            self.eat(TokenType.IDENTIFIER)
        pairs = [(names[0], alias)]
        while self.current.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            n = self._read_dotted_name()
            a = None
            if self.current.type == TokenType.AS:
                self.eat(TokenType.AS)
                a = self.current.value
                self.eat(TokenType.IDENTIFIER)
            pairs.append((n, a))
        return Import(pairs)

    def from_import_stmt(self):
        self.eat(TokenType.FROM)
        module = self._read_dotted_name()
        self.eat(TokenType.IMPORT)
        if self.current.type == TokenType.MULTIPLY:
            self.eat(TokenType.MULTIPLY)
            return FromImport(module, [("*", None)])
        paren = self.current.type == TokenType.LPAREN
        if paren:
            self.eat(TokenType.LPAREN)
        names = [self._read_import_name()]
        while self.current.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            if paren and self.current.type == TokenType.RPAREN:
                break
            names.append(self._read_import_name())
        if paren:
            self.eat(TokenType.RPAREN)
        return FromImport(module, names)

    def _read_dotted_name(self):
        name = self.current.value
        self.eat(TokenType.IDENTIFIER)
        while self.current.type == TokenType.DOT:
            self.eat(TokenType.DOT)
            name += "." + self.current.value
            self.eat(TokenType.IDENTIFIER)
        return name

    def _read_import_name(self):
        name  = self.current.value
        self.eat(TokenType.IDENTIFIER)
        alias = None
        if self.current.type == TokenType.AS:
            self.eat(TokenType.AS)
            alias = self.current.value
            self.eat(TokenType.IDENTIFIER)
        return (name, alias)

    def if_statement(self):
        self.eat(TokenType.IF)
        condition = self.expression()
        self.eat(TokenType.COLON)
        body          = self._parse_block()
        elif_clauses  = []
        else_body     = []
        while self.current.type == TokenType.ELIF:
            self.eat(TokenType.ELIF)
            cond = self.expression()
            self.eat(TokenType.COLON)
            elif_clauses.append((cond, self._parse_block()))
        if self.current.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.COLON)
            else_body = self._parse_block()
        return If(condition, body, elif_clauses, else_body)

    def while_statement(self):
        self.eat(TokenType.WHILE)
        condition = self.expression()
        self.eat(TokenType.COLON)
        body = self._parse_block()
        return While(condition, body)

    def for_statement(self):
        self.eat(TokenType.FOR)

        first_var = self.current.value
        self.eat(TokenType.IDENTIFIER)
        if self.current.type == TokenType.COMMA:
            vars_ = [first_var]
            while self.current.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                vars_.append(self.current.value)
                self.eat(TokenType.IDENTIFIER)
            var = vars_   
        else:
            var = first_var  

        self.eat(TokenType.IN)
        if (isinstance(var, str) and
                self.current.type == TokenType.IDENTIFIER and
                self.current.value == "range" and
                self.peek().type == TokenType.LPAREN):
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.LPAREN)
            args = [self.expression()]
            while self.current.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expression())
            self.eat(TokenType.RPAREN)
            if len(args) == 1:
                start, stop, step = Number("0"), args[0], None
            elif len(args) == 2:
                start, stop, step = args[0], args[1], None
            elif len(args) == 3:
                start, stop, step = args[0], args[1], args[2]
            else:
                raise SyntaxError("range() takes 1 to 3 arguments")
            self.eat(TokenType.COLON)
            return For(var, start, stop, step, self._parse_block())
        iterable = self.or_expr()
        self.eat(TokenType.COLON)
        return ForIn(var, iterable, self._parse_block())

    def try_statement(self):
        self.eat(TokenType.TRY)
        self.eat(TokenType.COLON)
        body       = self._parse_block()
        handlers   = []
        else_body  = []
        final_body = []
        while self.current.type == TokenType.EXCEPT:
            handlers.append(self._parse_except())
        if self.current.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.COLON)
            else_body = self._parse_block()
        if self.current.type == TokenType.FINALLY:
            self.eat(TokenType.FINALLY)
            self.eat(TokenType.COLON)
            final_body = self._parse_block()
        return TryExcept(body, handlers, else_body, final_body)

    def _parse_except(self):
        self.eat(TokenType.EXCEPT)
        exc_type = None
        name     = None
        if self.current.type not in (TokenType.COLON, TokenType.AS):
            exc_type = self._read_dotted_name()
        if self.current.type == TokenType.AS:
            self.eat(TokenType.AS)
            name = self.current.value
            self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.COLON)
        return ExceptHandler(exc_type, name, self._parse_block())

    def with_statement(self):
        self.eat(TokenType.WITH)
        expr  = self.expression()
        alias = None
        if self.current.type == TokenType.AS:
            self.eat(TokenType.AS)
            alias = self.current.value
            self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.COLON)
        return With(expr, alias, self._parse_block())

    def _parse_decorated(self):
        decorators = []
        while self.current.type == TokenType.AT:
            self.eat(TokenType.AT)
            name = self._read_dotted_name()
            if self.current.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                self._skip_to_rparen()
            self.skip_newlines()
            decorators.append(name)
        if self.current.type == TokenType.DEF:
            node = self.function_def()
        elif self.current.type == TokenType.CLASS:
            node = self.class_def()
        else:
            raise SyntaxError("Expected def or class after decorator")
        node.decorators = decorators
        return node

    def _skip_to_rparen(self):
        depth = 1
        while depth > 0 and self.current.type != TokenType.EOF:
            if self.current.type == TokenType.LPAREN:
                depth += 1
            elif self.current.type == TokenType.RPAREN:
                depth -= 1
            if depth > 0:
                self.position += 1
                self.current = self.tokens[self.position]
        self.eat(TokenType.RPAREN)

    def function_def(self):
        self.eat(TokenType.DEF)
        name = self.current.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)
        params, defaults, vararg, kwarg = self._parse_params()
        self.eat(TokenType.RPAREN)
        if self.current.type == TokenType.ARROW:
            self.eat(TokenType.ARROW)
            self.expression()           
        self.eat(TokenType.COLON)
        body = self._parse_block()
        return FunctionDef(name, params, body, defaults, vararg, kwarg)

    def _parse_params(self):
        params   = []
        defaults = {}
        vararg   = None
        kwarg    = None
        while self.current.type != TokenType.RPAREN:
            if self.current.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                if self.current.type == TokenType.IDENTIFIER:
                    vararg = self.current.value
                    self.eat(TokenType.IDENTIFIER)
            elif self.current.type == TokenType.POWER:
                self.eat(TokenType.POWER)
                kwarg = self.current.value
                self.eat(TokenType.IDENTIFIER)
            else:
                pname = self.current.value
                self.eat(TokenType.IDENTIFIER)
                if self.current.type == TokenType.COLON:
                    self.eat(TokenType.COLON)
                    self.expression()   
                params.append(pname)
                if self.current.type == TokenType.EQUALS:
                    self.eat(TokenType.EQUALS)
                    defaults[pname] = self.expression()
            if self.current.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
        return params, defaults, vararg, kwarg

    def class_def(self):
        self.eat(TokenType.CLASS)
        name  = self.current.value
        self.eat(TokenType.IDENTIFIER)
        bases = []
        if self.current.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            if self.current.type != TokenType.RPAREN:
                bases.append(self._read_dotted_name())
                while self.current.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current.type == TokenType.RPAREN:
                        break
                    bases.append(self._read_dotted_name())
            self.eat(TokenType.RPAREN)
        self.eat(TokenType.COLON)
        body = self._parse_block()
        return ClassDef(name, bases, body)

    def _parse_block(self):
        self.eat(TokenType.NEWLINE)
        self.eat(TokenType.INDENT)
        statements = []
        while self.current.type not in (TokenType.DEDENT, TokenType.EOF):
            self.skip_newlines()
            if self.current.type in (TokenType.DEDENT, TokenType.EOF):
                break
            statements.append(self.statement())
            if self.current.type == TokenType.NEWLINE:
                self.eat(TokenType.NEWLINE)
        self.eat(TokenType.DEDENT)
        return statements


    def expression(self):
        """Ternary: body if test else orelse"""
        node = self.or_expr()
        if self.current.type == TokenType.IF:
            self.eat(TokenType.IF)
            test   = self.or_expr()
            self.eat(TokenType.ELSE)
            orelse = self.expression()
            return Ternary(node, test, orelse)
        return node

    def or_expr(self):
        node = self.and_expr()
        while self.current.type == TokenType.OR:
            self.eat(TokenType.OR)
            node = BoolOp("or", [node, self.and_expr()])
        return node

    def and_expr(self):
        node = self.not_expr()
        while self.current.type == TokenType.AND:
            self.eat(TokenType.AND)
            node = BoolOp("and", [node, self.not_expr()])
        return node

    def not_expr(self):
        if self.current.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return UnaryOp("not", self.not_expr())
        return self.comparison()

    def comparison(self):
        node = self.bitwise_or()
        while True:
            t = self.current.type
            if t in (TokenType.DOUBLE_EQUALS, TokenType.NOT_EQUALS,
                     TokenType.LESS_THAN, TokenType.GREATER_THAN,
                     TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
                op = _Op(t)
                self.eat(t)
                node = BinaryOp(node, op, self.bitwise_or())
            elif t == TokenType.IN:
                self.eat(TokenType.IN)
                node = BinaryOp(node, _Op(TokenType.IN), self.bitwise_or())
            elif t == TokenType.NOT and self.peek().type == TokenType.IN:
                self.eat(TokenType.NOT)
                self.eat(TokenType.IN)
                node = UnaryOp("not", BinaryOp(node, _Op(TokenType.IN), self.bitwise_or()))
            elif t == TokenType.IS:
                self.eat(TokenType.IS)
                if self.current.type == TokenType.NOT:
                    self.eat(TokenType.NOT)
                    node = BinaryOp(node, _Op_named("IS_NOT"), self.bitwise_or())
                else:
                    node = BinaryOp(node, _Op_named("IS"), self.bitwise_or())
            else:
                break
        return node

    def bitwise_or(self):
        node = self.bitwise_xor()
        while self.current.type == TokenType.BITWISE_OR:
            self.eat(TokenType.BITWISE_OR)
            node = BinaryOp(node, _Op(TokenType.BITWISE_OR), self.bitwise_xor())
        return node

    def bitwise_xor(self):
        node = self.bitwise_and()
        while self.current.type == TokenType.BITWISE_XOR:
            self.eat(TokenType.BITWISE_XOR)
            node = BinaryOp(node, _Op(TokenType.BITWISE_XOR), self.bitwise_and())
        return node

    def bitwise_and(self):
        node = self.shift_expr()
        while self.current.type == TokenType.BITWISE_AND:
            self.eat(TokenType.BITWISE_AND)
            node = BinaryOp(node, _Op(TokenType.BITWISE_AND), self.shift_expr())
        return node

    def shift_expr(self):
        node = self.add_expr()
        while self.current.type in (TokenType.LSHIFT, TokenType.RSHIFT):
            op = _Op(self.current.type)
            self.eat(self.current.type)
            node = BinaryOp(node, op, self.add_expr())
        return node

    def add_expr(self):
        node = self.term()
        while self.current.type in _ADD_OPS:
            op = _Op(self.current.type)
            self.eat(self.current.type)
            node = BinaryOp(node, op, self.term())
        return node

    def term(self):
        node = self.unary()
        while self.current.type in _MUL_OPS:
            op = _Op(self.current.type)
            self.eat(self.current.type)
            node = BinaryOp(node, op, self.unary())
        return node

    def unary(self):
        if self.current.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp("-", self.unary())
        if self.current.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return self.unary()
        if self.current.type == TokenType.TILDE:
            self.eat(TokenType.TILDE)
            return UnaryOp("~", self.unary())
        return self.power()

    def power(self):
        node = self.postfix()
        if self.current.type == TokenType.POWER:
            self.eat(TokenType.POWER)
            node = BinaryOp(node, _Op(TokenType.POWER), self.unary())
        return node

    def postfix(self):
        node = self.primary()
        while True:
            if self.current.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                attr = self.current.value
                self.eat(TokenType.IDENTIFIER)
                if self.current.type == TokenType.LPAREN:
                    self.eat(TokenType.LPAREN)
                    args, kwargs = self._parse_args()
                    self.eat(TokenType.RPAREN)
                    node = MethodCall(node, attr, args, kwargs)
                else:
                    node = Attribute(node, attr)
            elif self.current.type == TokenType.LBRACKET:
                self.eat(TokenType.LBRACKET)
                if self.current.type == TokenType.COLON:
                    self.eat(TokenType.COLON)
                    upper = None if self.current.type in (TokenType.COLON, TokenType.RBRACKET) else self.expression()
                    step  = None
                    if self.current.type == TokenType.COLON:
                        self.eat(TokenType.COLON)
                        step = None if self.current.type == TokenType.RBRACKET else self.expression()
                    self.eat(TokenType.RBRACKET)
                    node = Subscript(node, Slice(None, upper, step))
                else:
                    idx = self.expression()
                    if self.current.type == TokenType.COLON:
                        self.eat(TokenType.COLON)
                        upper = None if self.current.type in (TokenType.COLON, TokenType.RBRACKET) else self.expression()
                        step  = None
                        if self.current.type == TokenType.COLON:
                            self.eat(TokenType.COLON)
                            step = None if self.current.type == TokenType.RBRACKET else self.expression()
                        self.eat(TokenType.RBRACKET)
                        node = Subscript(node, Slice(idx, upper, step))
                    else:
                        self.eat(TokenType.RBRACKET)
                        node = Subscript(node, idx)
            elif self.current.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args, kwargs = self._parse_args()
                self.eat(TokenType.RPAREN)
                if isinstance(node, Identifier):
                    node = FunctionCall(node.name, args, kwargs)
                else:
                    node = MethodCall(node, "__call__", args, kwargs)
            else:
                break
        return node

    def _parse_args(self):
        """Parse positional and keyword arguments."""
        args   = []
        kwargs = {}
        while self.current.type != TokenType.RPAREN:
            if self.current.type == TokenType.POWER:
                self.eat(TokenType.POWER)
                kwargs["__spread__"] = self.expression()
            elif self.current.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                args.append(UnaryOp("*spread*", self.expression()))
            elif (self.current.type == TokenType.IDENTIFIER and
                  self.peek().type == TokenType.EQUALS):
                kname = self.current.value
                self.eat(TokenType.IDENTIFIER)
                self.eat(TokenType.EQUALS)
                kwargs[kname] = self.expression()
            else:
                args.append(self.expression())
            if self.current.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
            else:
                break
        return args, kwargs

    def primary(self):
        token = self.current

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            if self.current.type == TokenType.RPAREN:
                self.eat(TokenType.RPAREN)
                return TupleLiteral([])
            node = self.expression()
            if self.current.type == TokenType.COMMA:
                elements = [node]
                while self.current.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current.type == TokenType.RPAREN:
                        break
                    elements.append(self.expression())
                self.eat(TokenType.RPAREN)
                return TupleLiteral(elements)
            self.eat(TokenType.RPAREN)
            return node
        if token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET)
            if self.current.type == TokenType.RBRACKET:
                self.eat(TokenType.RBRACKET)
                return ListLiteral([])
            first = self.expression()
            if self.current.type == TokenType.FOR:
                self.eat(TokenType.FOR)
                var = self.current.value
                self.eat(TokenType.IDENTIFIER)
                self.eat(TokenType.IN)
                iter_ = self.or_expr()   
                cond  = None
                if self.current.type == TokenType.IF:
                    self.eat(TokenType.IF)
                    cond = self.or_expr()  
                self.eat(TokenType.RBRACKET)
                return ListComp(first, var, iter_, cond)
            elements = [first]
            while self.current.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                if self.current.type == TokenType.RBRACKET:
                    break
                elements.append(self.expression())
            self.eat(TokenType.RBRACKET)
            return ListLiteral(elements)
        if token.type == TokenType.LBRACE:
            self.eat(TokenType.LBRACE)
            if self.current.type == TokenType.RBRACE:
                self.eat(TokenType.RBRACE)
                return DictLiteral([])
            first_key = self.expression()
            if self.current.type == TokenType.COLON:
                self.eat(TokenType.COLON)
                first_val = self.expression()
                pairs = [(first_key, first_val)]
                while self.current.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current.type == TokenType.RBRACE:
                        break
                    k = self.expression()
                    self.eat(TokenType.COLON)
                    v = self.expression()
                    pairs.append((k, v))
                self.eat(TokenType.RBRACE)
                return DictLiteral(pairs)
            else:
                elements = [first_key]
                while self.current.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    if self.current.type == TokenType.RBRACE:
                        break
                    elements.append(self.expression())
                self.eat(TokenType.RBRACE)
                return SetLiteral(elements)

        if token.type == TokenType.LAMBDA:
            self.eat(TokenType.LAMBDA)
            params = []
            if self.current.type != TokenType.COLON:
                params.append(self.current.value)
                self.eat(TokenType.IDENTIFIER)
                while self.current.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
                    params.append(self.current.value)
                    self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.COLON)
            body = self.expression()
            return Lambda(params, body)

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token.value)

        if token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token.value)

        if token.type == TokenType.FSTRING:
            self.eat(TokenType.FSTRING)
            return FString(token.value)

        if token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE);  return BoolLiteral(True)
        if token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE); return BoolLiteral(False)
        if token.type == TokenType.NONE:
            self.eat(TokenType.NONE);  return NoneLiteral()
        if token.type == TokenType.IDENTIFIER:
            name = token.value
            self.eat(TokenType.IDENTIFIER)
            return Identifier(name)
        if token.type == TokenType.PRINT:
            self.eat(TokenType.PRINT)
            if self.current.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args, kwargs = self._parse_args()
                self.eat(TokenType.RPAREN)
                return FunctionCall("print", args, kwargs)
            return Identifier("print")

        if token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp("-", self.primary())

        raise SyntaxError(
            f"Unexpected token {token.type.name} ({token.value!r}) at line {token.line}"
        )

def print_ast(node, indent=0):
    pad = "  " * indent
    n   = type(node).__name__
    if isinstance(node, Program):
        print(pad + "Program")
        for s in node.statements: print_ast(s, indent+1)
    elif isinstance(node, FunctionDef):
        print(pad + f"FunctionDef({node.name}, params={node.params})")
        for s in node.body: print_ast(s, indent+1)
    elif isinstance(node, ClassDef):
        print(pad + f"ClassDef({node.name}, bases={node.bases})")
        for s in node.body: print_ast(s, indent+1)
    elif isinstance(node, Assignment):
        print(pad + f"Assignment({node.name})")
        print_ast(node.value, indent+1)
    elif isinstance(node, ComplexAssignment):
        print(pad + "ComplexAssignment")
        print_ast(node.target, indent+1)
        print_ast(node.value, indent+1)
    elif isinstance(node, AugmentedAssignment):
        print(pad + f"AugAssign({node.op})")
        print_ast(node.target, indent+1)
        print_ast(node.value, indent+1)
    elif isinstance(node, Print):
        print(pad + "Print"); print_ast(node.expression, indent+1)
    elif isinstance(node, Return):
        print(pad + "Return")
        if node.value: print_ast(node.value, indent+1)
    elif isinstance(node, Raise):
        print(pad + "Raise")
        if node.exc: print_ast(node.exc, indent+1)
    elif isinstance(node, BinaryOp):
        print(pad + f"BinaryOp({node.op.name})")
        print_ast(node.left, indent+1); print_ast(node.right, indent+1)
    elif isinstance(node, UnaryOp):
        print(pad + f"UnaryOp({node.op})"); print_ast(node.operand, indent+1)
    elif isinstance(node, BoolOp):
        print(pad + f"BoolOp({node.op})")
        for v in node.values: print_ast(v, indent+1)
    elif isinstance(node, If):
        print(pad + "If"); print_ast(node.condition, indent+1)
        for s in node.body: print_ast(s, indent+1)
    elif isinstance(node, While):
        print(pad + "While"); print_ast(node.condition, indent+1)
        for s in node.body: print_ast(s, indent+1)
    elif isinstance(node, For):
        print(pad + f"For({node.var})")
    elif isinstance(node, ForIn):
        print(pad + f"ForIn({node.var})")
        print_ast(node.iterable, indent+1)
    elif isinstance(node, TryExcept):
        print(pad + "TryExcept")
    elif isinstance(node, FunctionCall):
        print(pad + f"Call({node.name})")
        for a in node.args: print_ast(a, indent+1)
    elif isinstance(node, MethodCall):
        print(pad + f"MethodCall(.{node.method})")
        print_ast(node.obj, indent+1)
    elif isinstance(node, Attribute):
        print(pad + f"Attribute(.{node.attr})"); print_ast(node.value, indent+1)
    elif isinstance(node, Subscript):
        print(pad + "Subscript"); print_ast(node.value, indent+1)
    elif isinstance(node, ListLiteral):
        print(pad + f"List({len(node.elements)} items)")
    elif isinstance(node, DictLiteral):
        print(pad + f"Dict({len(node.pairs)} pairs)")
    elif isinstance(node, TupleLiteral):
        print(pad + f"Tuple({len(node.elements)} items)")
    elif isinstance(node, Number):
        print(pad + f"Number({node.value})")
    elif isinstance(node, String):
        print(pad + f"String({node.value!r})")
    elif isinstance(node, FString):
        print(pad + f"FString({node.value!r})")
    elif isinstance(node, BoolLiteral):
        print(pad + f"Bool({node.value})")
    elif isinstance(node, NoneLiteral):
        print(pad + "None")
    elif isinstance(node, Identifier):
        print(pad + f"Id({node.name})")
    elif isinstance(node, Lambda):
        print(pad + f"Lambda({node.params})")
        print_ast(node.body, indent+1)
    elif isinstance(node, Ternary):
        print(pad + "Ternary")
        print_ast(node.test, indent+1)
    elif isinstance(node, (Pass, Break, Continue)):
        print(pad + n)
    elif isinstance(node, (Import, FromImport, Global, Nonlocal, Delete, Assert)):
        print(pad + n)
    else:
        print(pad + f"{n}")

if __name__ == "__main__":
    print("Enter Python code (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "": break
        lines.append(line)
    try:
        tokens = Lexer("\n".join(lines)).tokenize()
        ast    = Parser(tokens).parse()
        print("\n===== AST OUTPUT =====\n")
        print_ast(ast)
    except Exception as e:
        print("Error:", e)