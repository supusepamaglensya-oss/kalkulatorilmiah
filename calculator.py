import math
import re
import tkinter as tk
from tkinter import font as tkfont

# ---------- Palet warna (Navy & Putih) ----------
NAVY_DARK = "#0b1f3a"
NAVY = "#12294f"
NAVY_LIGHT = "#1c3a6b"
ACCENT = "#3d6fd6"
GOLD = "#e0a63e"
WHITE = "#ffffff"
GREY_TEXT = "#9fb1cc"
ERROR_RED = "#c0392b"


# ---------- Evaluasi ekspresi ----------
def build_names(deg: bool) -> dict:
    def trig(func):
        return lambda v: func(math.radians(v) if deg else v)

    def fact(v):
        if v != int(v):
            raise ValueError("faktorial hanya untuk bilangan bulat")
        return math.factorial(int(v))

    return {
        "sin": trig(math.sin),
        "cos": trig(math.cos),
        "tan": trig(math.tan),
        "log": math.log10,
        "ln": math.log,
        "sqrt": math.sqrt,
        "exp": math.exp,
        "fact": fact,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
    }


TOKEN_RE = re.compile(r"\d+\.?\d*|\.\d+|[A-Za-z_]+|\*\*|[^\sA-Za-z_\d]")


def add_implicit_multiplication(expr: str) -> str:
    """Ubah 2π -> 2*π, 2(3) -> 2*(3), (1+2)(3) -> (1+2)*(3), dst."""
    tokens = TOKEN_RE.findall(expr)
    out = []
    for tok in tokens:
        if out:
            prev = out[-1]
            prev_is_value = (
                prev[0].isdigit() or prev[0] == "." or prev == ")" or prev in ("pi", "e")
            )
            cur_is_start = tok[0].isdigit() or tok[0] == "." or tok[0].isalpha() or tok == "("
            if prev_is_value and cur_is_start:
                out.append("*")
        out.append(tok)
    return " ".join(out)


def evaluate(expr: str, deg: bool = True) -> str:
    if not expr.strip():
        return ""
    py_expr = (
        expr.replace("×", "*")
        .replace("÷", "/")
        .replace("^", "**")
        .replace("√", "sqrt")
        .replace("π", "pi")
        .replace("%", "/100")
    )
    try:
        py_expr = add_implicit_multiplication(py_expr)
        result = eval(py_expr, {"__builtins__": {}}, build_names(deg))
        if not isinstance(result, (int, float)) or isinstance(result, bool):
            return "Error"
        if isinstance(result, float):
            if math.isnan(result) or math.isinf(result):
                return "Error"
            result = round(result, 10)
            if result == int(result) and abs(result) < 1e15:
                result = int(result)
        return str(result)
    except ZeroDivisionError:
        return "Error: Bagi nol"
    except Exception:
        return "Error"


# ---------- GUI ----------
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Desktop")
        self.resizable(False, False)
        self.configure(bg=NAVY_DARK)

        self.expression = tk.StringVar(value="")
        self.deg_mode = tk.BooleanVar(value=True)
        self.memory = 0.0
        self.after_result = False  # True kalau layar sedang menampilkan hasil

        self._build_display()
        self._build_buttons()

        # Keyboard
        self.bind("<Return>", lambda e: self.on_button("=", "equals"))
        self.bind("<KP_Enter>", lambda e: self.on_button("=", "equals"))
        self.bind("<Escape>", lambda e: self.on_button("C", "clear"))
        self.entry.bind("<Key>", self._on_key)

    # ----- Display -----
    def _build_display(self):
        display_font = tkfont.Font(family="Consolas", size=26, weight="bold")
        mode_font = tkfont.Font(family="Consolas", size=10)

        header = tk.Frame(self, bg=NAVY_DARK)
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 0))

        tk.Label(
            header, text="KALKULATOR DESKTOP", font=("Consolas", 10, "bold"),
            bg=NAVY_DARK, fg=GREY_TEXT,
        ).pack(side="left")

        self.mode_label = tk.Label(header, text="DEG", font=mode_font, bg=NAVY_DARK, fg=GOLD)
        self.mode_label.pack(side="right")

        display_frame = tk.Frame(self, bg=WHITE, bd=0)
        display_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=12)

        self.entry = tk.Entry(
            display_frame,
            textvariable=self.expression,
            font=display_font,
            bg=WHITE,
            fg=NAVY_DARK,
            insertbackground=NAVY_DARK,
            relief="flat",
            justify="right",
            bd=0,
            width=16,
        )
        self.entry.pack(fill="x", ipady=18, padx=12)
        self.entry.focus_set()

    # ----- Buttons -----
    def _build_buttons(self):
        rows = [
            [("MC", "util", "mem_clear"), ("MR", "util", "mem_recall"), ("M+", "util", "mem_add"),
             ("M-", "util", "mem_sub"), ("DEG", "util", "toggle_mode")],
            [("sin", "fn", "func"), ("cos", "fn", "func"), ("tan", "fn", "func"),
             ("(", "fn", "char"), (")", "fn", "char")],
            [("log", "fn", "func"), ("ln", "fn", "func"), ("x!", "fn", "fact"),
             ("π", "fn", "char"), ("e", "fn", "char")],
            [("x^y", "fn", "char"), ("√", "fn", "func")],
            [("C", "op", "clear"), ("⌫", "op", "backspace"), ("%", "op", "char"),
             ("÷", "op", "char"), ("+/-", "op", "negate")],
            [("7", "num", "char"), ("8", "num", "char"), ("9", "num", "char"), ("×", "op", "char")],
            [("4", "num", "char"), ("5", "num", "char"), ("6", "num", "char"), ("-", "op", "char")],
            [("1", "num", "char"), ("2", "num", "char"), ("3", "num", "char"), ("+", "op", "char")],
        ]

        colors = {
            "num": (NAVY_LIGHT, WHITE, "#254a87"),
            "fn": (NAVY, GREY_TEXT, "#1c3a6b"),
            "op": (ACCENT, WHITE, "#5486e3"),
            "eq": (GOLD, NAVY_DARK, "#eeb85c"),
            "util": (NAVY, GOLD, "#1c3a6b"),
        }

        btn_font = tkfont.Font(family="Consolas", size=12, weight="bold")
        pad_font = tkfont.Font(family="Consolas", size=14, weight="bold")

        grid_frame = tk.Frame(self, bg=NAVY_DARK)
        grid_frame.grid(row=2, column=0, padx=16, pady=(0, 16))

        def make_btn(label, style, action, font=btn_font):
            bg, fg, active = colors[style]
            return tk.Button(
                grid_frame,
                text=label,
                font=font,
                bg=bg,
                fg=fg,
                activebackground=active,
                activeforeground=fg,
                relief="flat",
                bd=0,
                width=6,
                height=2,
                cursor="hand2",
                command=lambda l=label, a=action: self.on_button(l, a),
            )

        for r, row_defs in enumerate(rows):
            if len(row_defs) == 5:
                for c, (label, style, action) in enumerate(row_defs):
                    make_btn(label, style, action).grid(
                        row=r, column=c, padx=3, pady=3, sticky="nsew")
            elif len(row_defs) == 2:
                (l1, s1, a1), (l2, s2, a2) = row_defs
                make_btn(l1, s1, a1).grid(
                    row=r, column=0, columnspan=3, padx=3, pady=3, sticky="nsew")
                make_btn(l2, s2, a2).grid(
                    row=r, column=3, columnspan=2, padx=3, pady=3, sticky="nsew")
            else:
                for c, (label, style, action) in enumerate(row_defs[:3]):
                    make_btn(label, style, action).grid(
                        row=r, column=c, padx=3, pady=3, sticky="nsew")
                op_label, op_style, op_action = row_defs[3]
                make_btn(op_label, op_style, op_action).grid(
                    row=r, column=3, columnspan=2, padx=3, pady=3, sticky="nsew")

        last_r = len(rows)
        make_btn("0", "num", "char").grid(
            row=last_r, column=0, columnspan=2, padx=3, pady=3, sticky="nsew")
        make_btn(".", "num", "char").grid(
            row=last_r, column=2, padx=3, pady=3, sticky="nsew")
        make_btn("=", "eq", "equals", font=pad_font).grid(
            row=last_r, column=3, columnspan=2, padx=3, pady=3, sticky="nsew")

        for i in range(5):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="col")

    # ----- Logic -----
    def _on_key(self, event):
        """Ketikan dari keyboard: bersihkan layar kalau sedang Error / menampilkan hasil."""
        if event.char and event.char.isprintable():
            text = self.expression.get()
            if text.startswith("Error"):
                self.expression.set("")
            elif self.after_result and (event.char.isdigit() or event.char == "."):
                self.expression.set("")
        if event.keysym not in ("Return", "KP_Enter"):
            self.after_result = False

    def _set(self, text):
        self.expression.set(text)
        self.entry.icursor(tk.END)

    def on_button(self, label, action):
        text = self.expression.get()

        # Bersihkan pesan Error sebelum input baru
        if text.startswith("Error") and action not in ("toggle_mode", "mem_clear"):
            text = ""
            self._set("")

        # Mulai perhitungan baru kalau setelah hasil user menekan angka/fungsi
        if self.after_result and action in ("char", "func", "fact"):
            starts_new = label.isdigit() or label in (".", "π", "e", "(") or action in ("func", "fact")
            if starts_new:
                text = ""
                self._set("")

        if action == "char":
            mapping = {"x^y": "^"}
            self._set(text + mapping.get(label, label))
            self.after_result = False
        elif action == "func":
            fname = {"√": "sqrt"}.get(label, label)
            self._set(text + f"{fname}(")
            self.after_result = False
        elif action == "fact":
            self._set(text + "fact(")
            self.after_result = False
        elif action == "clear":
            self._set("")
            self.after_result = False
        elif action == "backspace":
            self._set(text[:-1])
            self.after_result = False
        elif action == "negate":
            self._negate(text)
        elif action == "equals":
            if text.strip():
                self._set(evaluate(text, self.deg_mode.get()))
                self.after_result = True
        elif action == "toggle_mode":
            self.deg_mode.set(not self.deg_mode.get())
            self.mode_label.config(text="DEG" if self.deg_mode.get() else "RAD")
        elif action in ("mem_clear", "mem_recall", "mem_add", "mem_sub"):
            self.handle_memory(action, text)

        self.entry.focus_set()

    def _negate(self, text):
        if not text:
            self._set("-")
        elif re.fullmatch(r"-?\d*\.?\d+", text):
            # angka biasa: cukup balik tandanya
            self._set(text[1:] if text.startswith("-") else "-" + text)
        elif text.startswith("-(") and text.endswith(")"):
            self._set(text[2:-1])
        else:
            # ekspresi: bungkus supaya seluruh ekspresi yang dinegasikan
            self._set(f"-({text})")
        self.after_result = False

    def handle_memory(self, action, text):
        if action == "mem_clear":
            self.memory = 0.0
        elif action == "mem_recall":
            if self.after_result:
                text = ""
            mem = self.memory
            mem_text = str(int(mem)) if mem == int(mem) else str(mem)
            self._set(text + mem_text)
            self.after_result = False
        else:
            result = evaluate(text, self.deg_mode.get())
            try:
                value = float(result)
            except ValueError:
                return
            self.memory += value if action == "mem_add" else -value


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()