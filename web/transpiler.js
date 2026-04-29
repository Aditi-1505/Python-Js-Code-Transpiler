class ASTNode {}

class NumberNode   extends ASTNode { constructor(v)        { super(); this.value = v; } }
class StringNode   extends ASTNode { constructor(v)        { super(); this.value = v; } }
class FStringNode  extends ASTNode { constructor(v)        { super(); this.value = v; } }
class BoolNode     extends ASTNode { constructor(v)        { super(); this.value = v; } }
class NoneNode     extends ASTNode { constructor()         { super(); } }

class Identifier   extends ASTNode { constructor(n)        { super(); this.name = n; } }
class Attribute    extends ASTNode { constructor(v, a)     { super(); this.value = v; this.attr = a; } }
class Subscript    extends ASTNode { constructor(v, i)     { super(); this.value = v; this.index = i; } }
class Slice        extends ASTNode {
  constructor(lower, upper, step) { super(); this.lower = lower; this.upper = upper; this.step = step; }
}

class ListLiteral  extends ASTNode { constructor(els)      { super(); this.elements = els; } }
class DictLiteral  extends ASTNode { constructor(pairs)    { super(); this.pairs = pairs; } }
class TupleLiteral extends ASTNode { constructor(els)      { super(); this.elements = els; } }
class SetLiteral   extends ASTNode { constructor(els)      { super(); this.elements = els; } }
class ListComp     extends ASTNode {
  constructor(elt, target, iter_, cond) { super(); this.elt = elt; this.target = target; this.iter_ = iter_; this.cond = cond; }
}

class BinaryOp     extends ASTNode { constructor(l, op, r) { super(); this.left = l; this.op = op; this.right = r; } }
class UnaryOp      extends ASTNode { constructor(op, o)    { super(); this.op = op; this.operand = o; } }
class BoolOp       extends ASTNode { constructor(op, vals) { super(); this.op = op; this.values = vals; } }
class Ternary      extends ASTNode { constructor(b, t, o)  { super(); this.body = b; this.test = t; this.orelse = o; } }
class Lambda       extends ASTNode { constructor(p, b)     { super(); this.params = p; this.body = b; } }
class FunctionCall extends ASTNode {
  constructor(n, a, kw = {}) { super(); this.name = n; this.args = a; this.kwargs = kw; }
}
class MethodCall   extends ASTNode {
  constructor(obj, m, a, kw = {}) { super(); this.obj = obj; this.method = m; this.args = a; this.kwargs = kw; }
}

class Program      extends ASTNode { constructor(stmts)    { super(); this.statements = stmts; } }
class Assignment   extends ASTNode { constructor(n, v)     { super(); this.name = n; this.value = v; } }
class ComplexAssignment extends ASTNode { constructor(t, v) { super(); this.target = t; this.value = v; } }
class AugmentedAssignment extends ASTNode { constructor(t, op, v) { super(); this.target = t; this.op = op; this.value = v; } }
class Print        extends ASTNode { constructor(e)        { super(); this.expression = e; } }
class Return       extends ASTNode { constructor(v)        { super(); this.value = v; } }
class Raise        extends ASTNode { constructor(e)        { super(); this.exc = e; } }
class Delete       extends ASTNode { constructor(t)        { super(); this.targets = t; } }
class Assert       extends ASTNode { constructor(t, m)     { super(); this.test = t; this.msg = m; } }
class Pass         extends ASTNode { constructor()         { super(); } }
class Break        extends ASTNode { constructor()         { super(); } }
class Continue     extends ASTNode { constructor()         { super(); } }
class Global       extends ASTNode { constructor(n)        { super(); this.names = n; } }
class Nonlocal     extends ASTNode { constructor(n)        { super(); this.names = n; } }

class If extends ASTNode {
  constructor(cond, body, elifs = [], elseBody = []) {
    super();
    this.condition    = cond;
    this.body         = body;
    this.elif_clauses = elifs;
    this.else_body    = elseBody;
  }
}
class While extends ASTNode {
  constructor(cond, body) { super(); this.condition = cond; this.body = body; }
}
class For extends ASTNode {
  constructor(v, start, stop, step, body) {
    super(); this.var = v; this.start = start; this.stop = stop; this.step = step; this.body = body;
  }
}
class ForIn extends ASTNode {
  constructor(v, iter, body) { super(); this.var = v; this.iterable = iter; this.body = body; }
}
class With extends ASTNode {
  constructor(expr, alias, body) { super(); this.expr = expr; this.alias = alias; this.body = body; }
}

class FunctionDef extends ASTNode {
  constructor(name, params, body, defaults = {}, vararg = null, kwarg = null, decorators = []) {
    super();
    this.name       = name;
    this.params     = params;
    this.body       = body;
    this.defaults   = defaults;
    this.vararg     = vararg;
    this.kwarg      = kwarg;
    this.decorators = decorators;
  }
}
class ClassDef extends ASTNode {
  constructor(name, bases, body, decorators = []) {
    super();
    this.name       = name;
    this.bases      = bases;
    this.body       = body;
    this.decorators = decorators;
  }
}

class TryExcept extends ASTNode {
  constructor(body, handlers, elseBody, finalBody) {
    super();
    this.body       = body;
    this.handlers   = handlers;
    this.else_body  = elseBody;
    this.final_body = finalBody;
  }
}
class ExceptHandler extends ASTNode {
  constructor(excType, name, body) {
    super(); this.exc_type = excType; this.name = name; this.body = body;
  }
}


class Import     extends ASTNode { constructor(n)    { super(); this.names = n; } }
class FromImport extends ASTNode { constructor(m, n) { super(); this.module = m; this.names = n; } }


function reviveAST(obj) {
  if (!obj || typeof obj !== 'object') return obj;
  if (Array.isArray(obj)) return obj.map(reviveAST);

  const r = reviveAST;   

  switch (obj.type) {
    case 'Program':
      return new Program((obj.statements || []).map(r));

    case 'Number':     case 'NumberNode':   return new NumberNode(obj.value);
    case 'String':     case 'StringNode':   return new StringNode(obj.value);
    case 'FString':    case 'FStringNode':  return new FStringNode(obj.value);
    case 'BoolLiteral':                     return new BoolNode(obj.value);
    case 'NoneLiteral':                     return new NoneNode();

    case 'Identifier':  return new Identifier(obj.name);
    case 'Attribute':   return new Attribute(r(obj.value), obj.attr);
    case 'Subscript':   return new Subscript(r(obj.value), r(obj.index));
    case 'Slice':       return new Slice(r(obj.lower), r(obj.upper), r(obj.step));

  
    case 'ListLiteral':  return new ListLiteral((obj.elements || []).map(r));
    case 'DictLiteral':
      return new DictLiteral((obj.pairs || []).map(([k, v]) => [r(k), r(v)]));
    case 'TupleLiteral': return new TupleLiteral((obj.elements || []).map(r));
    case 'SetLiteral':   return new SetLiteral((obj.elements || []).map(r));
    case 'ListComp':
      return new ListComp(r(obj.elt), obj.target, r(obj.iter_), obj.cond ? r(obj.cond) : null);

    
    case 'BinaryOp':    return new BinaryOp(r(obj.left), obj.op, r(obj.right));
    case 'UnaryOp':     return new UnaryOp(obj.op, r(obj.operand));
    case 'BoolOp':      return new BoolOp(obj.op, (obj.values || []).map(r));
    case 'Ternary':     return new Ternary(r(obj.body), r(obj.test), r(obj.orelse));
    case 'Lambda':      return new Lambda(obj.params, r(obj.body));
    case 'FunctionCall':
      return new FunctionCall(obj.name, (obj.args || []).map(r),
                              reviveKwargs(obj.kwargs));
    case 'MethodCall':
      return new MethodCall(r(obj.obj), obj.method, (obj.args || []).map(r),
                            reviveKwargs(obj.kwargs));

  
    case 'Assignment':        return new Assignment(obj.name, r(obj.value));
    case 'ComplexAssignment':  return new ComplexAssignment(r(obj.target), r(obj.value));
    case 'AugmentedAssignment':return new AugmentedAssignment(r(obj.target), obj.op, r(obj.value));
    case 'Print':             return new Print(r(obj.expression));
    case 'Return':            return new Return(obj.value ? r(obj.value) : null);
    case 'Raise':             return new Raise(obj.exc ? r(obj.exc) : null);
    case 'Delete':            return new Delete((obj.targets || []).map(r));
    case 'Assert':            return new Assert(r(obj.test), obj.msg ? r(obj.msg) : null);
    case 'Pass':              return new Pass();
    case 'Break':             return new Break();
    case 'Continue':          return new Continue();
    case 'Global':            return new Global(obj.names);
    case 'Nonlocal':          return new Nonlocal(obj.names);

   
    case 'If':
      return new If(
        r(obj.condition),
        (obj.body || []).map(r),
        (obj.elif_clauses || []).map(([c, b]) => [r(c), b.map(r)]),
        (obj.else_body || []).map(r)
      );
    case 'While':
      return new While(r(obj.condition), (obj.body || []).map(r));
    case 'For':
      return new For(obj.var, r(obj.start), r(obj.stop),
                     obj.step ? r(obj.step) : null, (obj.body || []).map(r));
    case 'ForIn':
      return new ForIn(obj.var, r(obj.iterable), (obj.body || []).map(r));
    case 'With':
      return new With(r(obj.expr), obj.alias, (obj.body || []).map(r));

    
    case 'FunctionDef':
      return new FunctionDef(
        obj.name, obj.params, (obj.body || []).map(r),
        reviveKwargs(obj.defaults), obj.vararg, obj.kwarg,
        obj.decorators || []
      );
    case 'ClassDef':
      return new ClassDef(obj.name, obj.bases || [], (obj.body || []).map(r),
                          obj.decorators || []);

   
    case 'TryExcept':
      return new TryExcept(
        (obj.body       || []).map(r),
        (obj.handlers   || []).map(r),
        (obj.else_body  || []).map(r),
        (obj.final_body || []).map(r)
      );
    case 'ExceptHandler':
      return new ExceptHandler(obj.exc_type, obj.name, (obj.body || []).map(r));


    case 'Import':
      return new Import(obj.names);
    case 'FromImport':
      return new FromImport(obj.module, obj.names);

    default:
      return obj;   
  }
}

function reviveKwargs(kwargs) {
  if (!kwargs || typeof kwargs !== 'object') return {};
  const out = {};
  for (const [k, v] of Object.entries(kwargs)) {
    out[k] = reviveAST(v);
  }
  return out;
}


async function runPipeline(sourceCode) {
  let raw;
  try {
    const resp = await fetch('/api/transpile', {
      method:      'POST',
      headers:     { 'Content-Type': 'application/json' },
      body:        JSON.stringify({ source: sourceCode }),
      credentials: 'include',
    });

    if (!resp.ok) {
      return {
        tokens: null, ast: null, symbolTable: null,
        jsCode: null,
        unsupported: [], error: {
          stage:   'Network',
          message: `Server returned ${resp.status} ${resp.statusText}`,
        },
      };
    }

    raw = await resp.json();
  } catch (err) {
    return {
      tokens: null, ast: null, symbolTable: null,
      jsCode: null,
      unsupported: [], error: {
        stage:   'Network',
        message: `Could not reach the backend: ${err.message}`,
      },
    };
  }

  if (raw.ast) raw.ast = reviveAST(raw.ast);

  return raw;
}


function formatTokens(tokens) {
  if (!tokens || !tokens.length) return 'No tokens.';

  const rows = tokens
    .filter(t => !['EOF', 'COMMENT'].includes(t.type))
    .map(t =>
      `${String(t.type).padEnd(25)} ${String(t.value).padEnd(20)} line ${t.line}`
    );

  const header = `${'TYPE'.padEnd(25)} ${'VALUE'.padEnd(20)} POSITION`;
  const divider = '-'.repeat(60);
  return `${header}\n${divider}\n${rows.join('\n')}`;
}


function formatSymbolTable(table) {
  if (!table || !Object.keys(table).length) return 'Empty symbol table.';
  const rows = Object.entries(table)
    .sort(([, a], [, b]) => a.localeCompare(b) || 0)
    .map(([name, kind]) => `${name.padEnd(30)} ${kind}`);
  return `${'NAME'.padEnd(30)} TYPE\n${'-'.repeat(40)}\n${rows.join('\n')}`;
}


if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    Program, NumberNode, StringNode, FStringNode, BoolNode, NoneNode,
    Identifier, Attribute, Subscript, Slice,
    ListLiteral, DictLiteral, TupleLiteral, SetLiteral, ListComp,
    BinaryOp, UnaryOp, BoolOp, Ternary, Lambda, FunctionCall, MethodCall,
    Assignment, ComplexAssignment, AugmentedAssignment,
    Print, Return, Raise, Delete, Assert, Pass, Break, Continue,
    Global, Nonlocal,
    If, While, For, ForIn, With,
    FunctionDef, ClassDef, TryExcept, ExceptHandler,
    Import, FromImport,
    reviveAST, runPipeline, formatTokens, formatSymbolTable,
  };
}
