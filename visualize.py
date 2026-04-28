import tkinter as tk
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from lexer import Lexer
from parser import Parser, print_ast

from semantic import SemanticAnalyzer

BG        = "#f5f0eb"
SURFACE   = "#fffcf8"
PANEL_HDR = "#f0ebe3"
BORDER    = "#ddd6cc"
TEXT      = "#2d2926"
TEXT_DIM  = "#8c7f74"
TEXT_BRT  = "#1a1410"
ACCENT    = "#3d7ebf"
ACCENT2   = "#7b52ab"
ACCENT3   = "#c87d2f"
ERROR_FG  = "#b83232"
ERROR_BG  = "#fdf0f0"
EDGE_RAW  = "#bbb0a4"

NODE_COLORS = {
   
    "Program":              "#5b9bd5",
    "FunctionDef":          "#e05c9a",
    "ClassDef":             "#26a69a",
    "Lambda":               "#00897b",
    
    "Assignment":           "#9b72c8",
    "ComplexAssignment":    "#7c5cbf",
    "AugmentedAssignment":  "#8d6ab8",
    "Print":                "#4aaa82",
    "Return":               "#e57373",
    "Raise":                "#ef5350",
    "Delete":               "#d84315",
    "Assert":               "#ff8a65",
    "Pass":                 "#90a4ae",
    "Break":                "#78909c",
    "Continue":             "#546e7a",
    "Global":               "#a1887f",
    "Nonlocal":             "#8d6e63",
    "Import":               "#78909c",
    "FromImport":           "#607d8b",
    
    "If":                   "#d05050",
    "While":                "#c4648a",
    "For":                  "#7a6ebf",
    "ForIn":                "#6a5fbf",
    "With":                 "#5c7abf",
    "TryExcept":            "#c0784a",
    "ExceptHandler":        "#bf6a3a",
    
    "BinaryOp":             "#d4902a",
    "UnaryOp":              "#c47820",
    "BoolOp":               "#b86820",
    "Ternary":              "#e09030",
    "FunctionCall":         "#3aacbc",
    "MethodCall":           "#2a9aac",
    "Attribute":            "#5b8fbf",
    "Subscript":            "#4a7faf",
    "ListComp":             "#43a869",
    
    "Number":               "#63b58a",
    "String":               "#c4a030",
    "FString":              "#b89020",
    "BoolLiteral":          "#5b9b7a",
    "NoneLiteral":          "#9e9e9e",
    "ListLiteral":          "#4caf7a",
    "DictLiteral":          "#bf7040",
    "TupleLiteral":         "#7a8fbf",
    "SetLiteral":           "#bf5080",
    "Identifier":           "#7097c4",
    "Slice":                "#8899bb",
}

OP_SYMBOL = {
    "PLUS": "+",
    "MINUS": "-",
    "MULTIPLY": "x",
    "DIVIDE": "/",
    "FLOOR_DIVIDE": "//",
    "MODULO": "%",
    "DOUBLE_EQUALS": "==",
    "NOT_EQUALS": "!=",
    "LESS_THAN": "<",
    "GREATER_THAN": ">",
    "LESS_EQUAL": "<=",
    "GREATER_EQUAL": ">=",
}

NW = 118
NH = 44
H_GAP = 20
V_GAP = 50

def get_children(node):
   
    if isinstance(node, Program):
        return node.statements
    if isinstance(node, FunctionDef):
        return list(node.body)
    if isinstance(node, ClassDef):
        return list(node.body)
    if isinstance(node, Lambda):
        return [node.body]
    
    if isinstance(node, Assignment):
        return [node.value]
    if isinstance(node, ComplexAssignment):
        return [node.target, node.value]
    if isinstance(node, AugmentedAssignment):
        return [node.target, node.value]
    if isinstance(node, Print):
        return [node.expression]
    if isinstance(node, Return):
        return [node.value] if node.value else []
    if isinstance(node, Raise):
        return [node.exc] if node.exc else []
    if isinstance(node, Delete):
        return list(node.targets)
    if isinstance(node, Assert):
        return ([node.test, node.msg] if node.msg else [node.test])
   
    if isinstance(node, If):
        kids = [node.condition] + list(node.body)
        for cond, body in node.elif_clauses:
            kids += [cond] + list(body)
        kids += list(node.else_body)
        return kids
    if isinstance(node, While):
        return [node.condition] + list(node.body)
    if isinstance(node, For):
        parts = [node.start, node.stop]
        if node.step:
            parts.append(node.step)
        return parts + list(node.body)
    if isinstance(node, ForIn):
        return [node.iterable] + list(node.body)
    if isinstance(node, With):
        return [node.expr] + list(node.body)
    if isinstance(node, TryExcept):
        kids = list(node.body) + list(node.handlers)
        kids += list(node.else_body) + list(node.final_body)
        return kids
    if isinstance(node, ExceptHandler):
        return list(node.body)
    
    if isinstance(node, BinaryOp):
        return [node.left, node.right]
    if isinstance(node, UnaryOp):
        return [node.operand]
    if isinstance(node, BoolOp):
        return list(node.values)
    if isinstance(node, Ternary):
        return [node.test, node.body, node.orelse]
    if isinstance(node, FunctionCall):
        return list(node.args)
    if isinstance(node, MethodCall):
        return [node.obj] + list(node.args)
    if isinstance(node, Attribute):
        return [node.value]
    if isinstance(node, Subscript):
        return [node.value, node.index]
    if isinstance(node, Slice):
        return [x for x in [node.lower, node.upper, node.step] if x]
    if isinstance(node, ListComp):
        kids = [node.elt, node.iter_]
        if node.cond:
            kids.append(node.cond)
        return kids
   
    if isinstance(node, (ListLiteral, TupleLiteral, SetLiteral)):
        return list(node.elements)
    if isinstance(node, DictLiteral):
        return [x for pair in node.pairs for x in pair]
    return []

def node_labels(node):
    
    if isinstance(node, Program):
        return "Program", ""
    if isinstance(node, FunctionDef):
        params = ", ".join(node.params)
        return "def", f"{node.name}({params})"
    if isinstance(node, ClassDef):
        bases = ", ".join(node.bases) if node.bases else ""
        return "class", f"{node.name}" + (f"({bases})" if bases else "")
    if isinstance(node, Lambda):
        params = ", ".join(node.params)
        return "lambda", params
    
    if isinstance(node, Assignment):
        name = node.name if isinstance(node.name, str) else str(node.name)
        return "Assign", name
    if isinstance(node, ComplexAssignment):
        return "Assign", ""
    if isinstance(node, AugmentedAssignment):
        op_str = getattr(node.op, "name", str(node.op))
        return "AugAssign", op_str
    if isinstance(node, Print):
        return "Print", ""
    if isinstance(node, Return):
        return "Return", ""
    if isinstance(node, Raise):
        return "Raise", ""
    if isinstance(node, Delete):
        return "Delete", ""
    if isinstance(node, Assert):
        return "Assert", ""
    if isinstance(node, Pass):
        return "Pass", ""
    if isinstance(node, Break):
        return "Break", ""
    if isinstance(node, Continue):
        return "Continue", ""
    if isinstance(node, Global):
        return "Global", ", ".join(node.names)
    if isinstance(node, Nonlocal):
        return "Nonlocal", ", ".join(node.names)
    if isinstance(node, Import):
        names = ", ".join(n if isinstance(n, str) else n[0] for n in node.names)
        return "Import", names
    if isinstance(node, FromImport):
        return "From", node.module
    
    if isinstance(node, If):
        return "If", ""
    if isinstance(node, While):
        return "While", ""
    if isinstance(node, For):
        var_label = node.var if isinstance(node.var, str) else ", ".join(node.var)
        return "For", var_label
    if isinstance(node, ForIn):
        var_label = node.var if isinstance(node.var, str) else ", ".join(node.var)
        return "ForIn", var_label
    if isinstance(node, With):
        alias = f" as {node.alias}" if node.alias else ""
        return "With", alias.strip()
    if isinstance(node, TryExcept):
        return "Try", ""
    if isinstance(node, ExceptHandler):
        exc = node.exc_type or "Exception"
        label = f"{exc}" + (f" as {node.name}" if node.name else "")
        return "Except", label
   
    if isinstance(node, BinaryOp):
        sym = OP_SYMBOL.get(node.op.name, node.op.name)
        return "BinaryOp", sym
    if isinstance(node, UnaryOp):
        return "UnaryOp", str(node.op)
    if isinstance(node, BoolOp):
        return "BoolOp", str(node.op)
    if isinstance(node, Ternary):
        return "Ternary", ""
    if isinstance(node, FunctionCall):
        name = node.name if isinstance(node.name, str) else "call"
        return "Call", name
    if isinstance(node, MethodCall):
        return "MethodCall", f".{node.method}"
    if isinstance(node, Attribute):
        return "Attr", f".{node.attr}"
    if isinstance(node, Subscript):
        return "Subscript", ""
    if isinstance(node, Slice):
        return "Slice", ""
    if isinstance(node, ListComp):
        return "ListComp", ""
   
    if isinstance(node, Number):
        return "Number", str(node.value)
    if isinstance(node, String):
        return "String", f'"{node.value}"'
    if isinstance(node, FString):
        return "FString", f'f"{node.value}"'
    if isinstance(node, BoolLiteral):
        return "Bool", str(node.value)
    if isinstance(node, NoneLiteral):
        return "None", ""
    if isinstance(node, ListLiteral):
        return "List", f"{len(node.elements)} items"
    if isinstance(node, DictLiteral):
        return "Dict", f"{len(node.pairs)} pairs"
    if isinstance(node, TupleLiteral):
        return "Tuple", f"{len(node.elements)} items"
    if isinstance(node, SetLiteral):
        return "Set", f"{len(node.elements)} items"
    if isinstance(node, Identifier):
        return "Ident", node.name
    return type(node).__name__, ""

class LayoutNode:
    __slots__ = ("ast", "kids", "width", "x", "y")

    def __init__(self, ast_node, kids):
        self.ast = ast_node
        self.kids = kids
        self.width = 0
        self.x = 0
        self.y = 0

def build_layout(node):
    kids = [build_layout(c) for c in get_children(node)]
    lay = LayoutNode(node, kids)
    if not kids:
        lay.width = NW
    else:
        total = sum(k.width for k in kids) + H_GAP * (len(kids) - 1)
        lay.width = max(NW, total)
    return lay

def assign_x(lay, left=0):
    if not lay.kids:
        lay.x = left + lay.width // 2
        return
    cx = left
    for k in lay.kids:
        assign_x(k, cx)
        cx += k.width + H_GAP
    lay.x = (lay.kids[0].x + lay.kids[-1].x) // 2

def flatten(lay, y=0, out=None):
    if out is None:
        out = []
    lay.y = y
    out.append(lay)
    for k in lay.kids:
        flatten(k, y + NH + V_GAP, out)
    return out

FONT_NODE  = ("Helvetica", 10, "bold")
FONT_SUB   = ("Helvetica", 9)
FONT_TIP   = ("Helvetica", 9)
FONT_UI    = ("Helvetica", 10)
FONT_UI_B  = ("Helvetica", 10, "bold")
FONT_SMALL = ("Helvetica", 8)
FONT_CODE  = ("Courier New", 12)

def draw_tree(canvas, ast_root):
    canvas.delete("all")
    if ast_root is None:
        canvas.create_text(24, 24, text="(nothing to show)",
                           fill=TEXT_DIM, anchor="nw", font=FONT_UI)
        return

    lay = build_layout(ast_root)
    assign_x(lay, 24)
    nodes = flatten(lay, y=24)
    max_x = max(n.x + NW // 2 for n in nodes) + 36
    max_y = max(n.y + NH for n in nodes) + 36
    canvas.config(scrollregion=(0, 0, max_x, max_y))
    canvas.update_idletasks()

    for n in nodes:
        for k in n.kids:
            x1, y1 = n.x, n.y + NH
            x2, y2 = k.x, k.y
            mid_y = (y1 + y2) // 2
            canvas.create_line(x1, y1, x1, mid_y, x2, mid_y, x2, y2,
                               fill=EDGE_RAW, width=1.5)

    for n in nodes:
        col = NODE_COLORS.get(type(n.ast).__name__, "#aaaaaa")
        rx = n.x - NW // 2
        ry = n.y
        tag = f"n{id(n)}"

        canvas.create_rectangle(rx + 3, ry + 3, rx + NW + 3, ry + NH + 3,
                                 fill="#ccc4ba", outline="")
        canvas.create_rectangle(rx, ry, rx + NW, ry + NH,
                                 fill=col, outline="#f1dada", width=1, tags=tag)

        top, sub = node_labels(n.ast)
        cx = rx + NW // 2
        if sub:
            canvas.create_text(cx, ry + 14, text=top,
                               fill="#ffffff", font=FONT_NODE, tags=tag)
            sub_disp = sub if len(sub) <= 14 else sub[:13] + "..."
            canvas.create_text(cx, ry + 30, text=sub_disp,
                               fill="#c8a7a7", font=FONT_SUB, tags=tag)
        else:
            canvas.create_text(cx, ry + 22, text=top,
                               fill="#ffffff", font=FONT_NODE, tags=tag)

        _bind_tooltip(canvas, tag, n.ast)

_tip_win = None

def _bind_tooltip(canvas, tag, node):
    def on_enter(e):
        global _tip_win
        _hide_tooltip()
        lines = [f"Type:   {type(node).__name__}"]
        if isinstance(node, FunctionDef):
            lines.append(f"Name:   {node.name}")
            lines.append(f"Params: {', '.join(node.params) or '(none)'}")
            if node.vararg:  lines.append(f"*args:  {node.vararg}")
            if node.kwarg:   lines.append(f"**kw:   {node.kwarg}")
        elif isinstance(node, ClassDef):
            lines.append(f"Name:   {node.name}")
            if node.bases: lines.append(f"Bases:  {', '.join(node.bases)}")
        elif isinstance(node, (Assignment, FunctionCall)):
            lines.append(f"Name:   {node.name}")
        elif isinstance(node, MethodCall):
            lines.append(f"Method: .{node.method}")
        elif isinstance(node, Attribute):
            lines.append(f"Attr:   .{node.attr}")
        elif isinstance(node, (Number, String, FString, BoolLiteral)):
            lines.append(f"Value:  {node.value}")
        elif isinstance(node, Identifier):
            lines.append(f"Name:   {node.name}")
        elif isinstance(node, BinaryOp):
            sym = OP_SYMBOL.get(node.op.name, node.op.name)
            lines.append(f"Op:     {sym}  ({node.op.name})")
        elif isinstance(node, UnaryOp):
            lines.append(f"Op:     {node.op}")
        elif isinstance(node, BoolOp):
            lines.append(f"Op:     {node.op}")
        elif isinstance(node, AugmentedAssignment):
            lines.append(f"Op:     {getattr(node.op, 'name', node.op)}")
        elif isinstance(node, (For, ForIn)):
            var_label = node.var if isinstance(node.var, str) else ", ".join(node.var)
            lines.append(f"Var:    {var_label}")
        elif isinstance(node, ExceptHandler):
            if node.exc_type: lines.append(f"Type:   {node.exc_type}")
            if node.name:     lines.append(f"As:     {node.name}")
        elif isinstance(node, (Import, FromImport)):
            if isinstance(node, FromImport):
                lines.append(f"Module: {node.module}")
        elif isinstance(node, (Global, Nonlocal)):
            lines.append(f"Names:  {', '.join(node.names)}")
        _tip_win = tk.Toplevel(canvas)
        _tip_win.wm_overrideredirect(True)
        _tip_win.configure(bg=BORDER)
        outer = tk.Frame(_tip_win, bg=BORDER, padx=1, pady=1)
        outer.pack()
        inner = tk.Frame(outer, bg=SURFACE, padx=10, pady=8)
        inner.pack()
        tk.Label(inner, text="\n".join(lines), font=FONT_TIP,
                 bg=SURFACE, fg=TEXT, justify="left").pack()
        x = canvas.winfo_rootx() + e.x + 16
        y = canvas.winfo_rooty() + e.y - 8
        _tip_win.geometry(f"+{x}+{y}")
    canvas.tag_bind(tag, "<Enter>", on_enter)
    canvas.tag_bind(tag, "<Leave>", lambda e: _hide_tooltip())

def _hide_tooltip():
    global _tip_win
    if _tip_win:
        try:
            _tip_win.destroy()
        except Exception:
            pass
        _tip_win = None

SAMPLE = """\
x = 5 + 3
y = x * 1
z = 10 + 0

print(x)
print(y + 0)
if x > 2:
    print(x)
elif z == 10:
    print(z)
else:
    print(0)
for i in range(3):
    print(i)
"""

class ASTVisualizerApp(tk.Tk):
    def __init__(self, source_code=None):
        super().__init__()
        self.title("AST Visualizer")
        self.geometry("1320x800")
        self.minsize(900, 600)
        self.configure(bg=BG)
        self._build_ui()
        self.__dict__["editor"] = self._text
        self.__dict__["canvas"] = self._canvas_raw

        
        if source_code:
            self._text.delete("1.0", "end")
            self._text.insert("1.0", source_code)
            self.after(150, self._run)
        else:
            self._text.insert("1.0", SAMPLE.strip())

    def _build_ui(self):
        self._build_header()
        body = tk.PanedWindow(self, orient="horizontal",
                              bg=BORDER, sashwidth=5, sashrelief="flat")
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg=SURFACE)
        body.add(left, minsize=260, width=300)
        self._build_editor_panel(left)
        right = tk.Frame(body, bg=BG)
        body.add(right, minsize=500)
        self._build_tree_panel(right)

    def _build_header(self):
        bar = tk.Frame(self, bg=SURFACE, height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=BORDER, height=1).place(relx=0, rely=1.0,
                                                  relwidth=1, anchor="sw")
        tk.Label(bar, text="AST Visualizer", bg=SURFACE, fg=TEXT_BRT,
                 font=("Helvetica", 14, "bold")).pack(side="left", padx=18, pady=14)
        self._status_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self._status_var,
                 bg=SURFACE, fg=TEXT_DIM, font=FONT_UI).pack(side="right", padx=18)
        tk.Label(bar, text="Ctrl+Enter to run",
                 bg=SURFACE, fg=TEXT_DIM, font=FONT_SMALL).pack(side="right", padx=2)

    def _build_editor_panel(self, parent):
        tk.Label(parent, text="Source code", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_SMALL, anchor="w", pady=7).pack(fill="x", padx=14)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        edit_frame = tk.Frame(parent, bg=SURFACE)
        edit_frame.pack(fill="both", expand=True)

        self._text = tk.Text(
            edit_frame, bg=SURFACE, fg=TEXT,
            insertbackground=ACCENT,
            font=FONT_CODE, relief="flat", bd=0,
            wrap="none", padx=12, pady=10,
            selectbackground="#c8dff4",
            undo=True,
        )
        sb = tk.Scrollbar(edit_frame, orient="vertical", command=self._text.yview)
        self._text.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._text.pack(fill="both", expand=True)
        self._text.bind("<Tab>",
            lambda e: (self._text.insert("insert", "    "), "break")[1])

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        btn_bar = tk.Frame(parent, bg=SURFACE, pady=10, padx=14)
        btn_bar.pack(fill="x")
        tk.Button(
            btn_bar, text="Clear", command=self._clear,
            bg=PANEL_HDR, fg=TEXT_DIM, activebackground=BORDER,
            font=FONT_UI, relief="flat", padx=12, pady=6, bd=0,
        ).pack(side="left")
        tk.Button(
            btn_bar, text="Visualize  >", command=self._run,
            bg=ACCENT, fg="white", activebackground="#2d6aad",
            activeforeground="white", font=FONT_UI_B,
            relief="flat", padx=14, pady=6, bd=0,
        ).pack(side="right")

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")
        leg = tk.Frame(parent, bg=SURFACE, padx=14, pady=10)
        leg.pack(fill="x")
        tk.Label(leg, text="Node types", bg=SURFACE, fg=TEXT_DIM,
                 font=FONT_SMALL).pack(anchor="w", pady=(0, 5))
        LEGEND_GROUPS = [
            ("Structure",     ["Program", "FunctionDef", "ClassDef", "Lambda"]),
            ("Statements",    ["Assignment", "AugmentedAssignment", "Print",
                               "Return", "Raise", "Assert", "Pass", "Break", "Continue"]),
            ("Control Flow",  ["If", "While", "For", "ForIn", "With", "TryExcept", "ExceptHandler"]),
            ("Expressions",   ["BinaryOp", "UnaryOp", "BoolOp", "FunctionCall",
                               "MethodCall", "Attribute", "Subscript"]),
            ("Literals",      ["Number", "String", "FString", "BoolLiteral",
                               "NoneLiteral", "ListLiteral", "DictLiteral",
                               "TupleLiteral", "Identifier"]),
        ]
        for group_name, names in LEGEND_GROUPS:
            tk.Label(leg, text=group_name, bg=SURFACE, fg=TEXT_DIM,
                     font=("Helvetica", 7, "bold")).pack(anchor="w", pady=(4, 1))
            grid = tk.Frame(leg, bg=SURFACE)
            grid.pack(anchor="w")
            for i, name in enumerate(names):
                col = NODE_COLORS.get(name, "#aaaaaa")
                row, col_idx = divmod(i, 2)
                fr = tk.Frame(grid, bg=SURFACE)
                fr.grid(row=row, column=col_idx, sticky="w", padx=(0, 10), pady=1)
                tk.Canvas(fr, width=10, height=10, bg=col,
                          highlightthickness=0).pack(side="left")
                tk.Label(fr, text=f"  {name}", bg=SURFACE, fg=TEXT_DIM,
                         font=FONT_SMALL).pack(side="left")

    def _build_tree_panel(self, parent):
        hdr = tk.Frame(parent, bg=PANEL_HDR, pady=7)
        hdr.pack(fill="x")
        tk.Label(hdr, text="AST", bg=PANEL_HDR, fg=TEXT,
                 font=FONT_UI_B, padx=14).pack(side="left")
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(fill="both", expand=True)
        cv = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        vsb = tk.Scrollbar(wrap, orient="vertical",   command=cv.yview)
        hsb = tk.Scrollbar(wrap, orient="horizontal", command=cv.xview)
        cv.config(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        cv.pack(fill="both", expand=True)

        cv.bind("<MouseWheel>",
                lambda e, c=cv: c.yview_scroll(-1 * (e.delta // 120), "units"))
        cv.bind("<Button-4>", lambda e, c=cv: c.yview_scroll(-1, "units"))
        cv.bind("<Button-5>", lambda e, c=cv: c.yview_scroll( 1, "units"))
        cv.bind("<ButtonPress-1>", lambda e, c=cv: c.scan_mark(e.x, e.y))
        cv.bind("<B1-Motion>",     lambda e, c=cv: c.scan_dragto(e.x, e.y, gain=1))

        self._canvas_raw = cv

    def _clear(self):
        self._text.delete("1.0", "end")
        self._canvas_raw.delete("all")
        self._status_var.set("")

    def _run(self):
        code = self._text.get("1.0", "end").rstrip()
        if not code:
            return
        try:
            tokens = Lexer(code).tokenize()
            raw_ast = Parser(tokens).parse()
            SemanticAnalyzer().analyze(raw_ast)
            draw_tree(self._canvas_raw, raw_ast)
            self._status_var.set("Parsed successfully")
        except Exception as exc:
            self._show_error(str(exc))
            self._status_var.set(f"Error: {exc}")

    def _show_error(self, msg):
        self._canvas_raw.delete("all")
        self._canvas_raw.create_rectangle(20, 20, 660, 110,
                             fill=ERROR_BG, outline="#e8b0b0", width=1)
        self._canvas_raw.create_text(32, 36, text="Error", fill=ERROR_FG,
                       font=FONT_UI_B, anchor="nw")
        self._canvas_raw.create_text(32, 58, text=msg, fill=ERROR_FG,
                       font=FONT_UI, anchor="nw", width=600)

if __name__ == "__main__":
    app = ASTVisualizerApp()
    app.bind("<Control-Return>", lambda e: app._run())
    app.mainloop()
