import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import random

PRESETS = {
    "Кривая Коха": {"axiom": "F", "angle": 60, "dir": 0, "rules": {"F": "F+F--F+F"}, "iter": 4},
    "Ковровое дерево": {"axiom": "F", "angle": 90, "dir": 0, "rules": {"F": "F[+F]F[-F]F"}, "iter": 3},
    "Дракон": {"axiom": "FX", "angle": 90, "dir": 0, "rules": {"X": "X+YF+", "Y": "-FX-Y"}, "iter": 10},
    "Фрактальное дерево (1б)": {"axiom": "F", "angle": 25, "dir": 90, "rules": {"F": "FF-[-F+F+F]+[+F-F-F]"}, "iter": 4, "is_tree": True}
}

class LSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("L-системы и Фрактальные деревья")
        self.root.geometry("900x700")

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        ctrl_frame = ttk.Frame(root)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(ctrl_frame, text="Пресет:").pack(side=tk.LEFT, padx=5)
        self.preset_var = tk.StringVar(value="Фрактальное дерево (1б)")
        preset_menu = ttk.Combobox(ctrl_frame, textvariable=self.preset_var, values=list(PRESETS.keys()), state="readonly", width=25)
        preset_menu.pack(side=tk.LEFT, padx=5)
        preset_menu.bind("<<ComboboxSelected>>", self.load_preset)

        ttk.Label(ctrl_frame, text="Итерации:").pack(side=tk.LEFT, padx=5)
        self.iter_var = tk.IntVar(value=4)
        ttk.Spinbox(ctrl_frame, from_=1, to=12, textvariable=self.iter_var, width=5).pack(side=tk.LEFT)

        ttk.Label(ctrl_frame, text="Случайность:").pack(side=tk.LEFT, padx=5)
        self.rand_var = tk.DoubleVar(value=0.0)
        ttk.Scale(ctrl_frame, from_=0.0, to=15.0, variable=self.rand_var, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(ctrl_frame, text="Загрузить из файла", command=self.load_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="Построить", command=self.draw).pack(side=tk.LEFT, padx=5)

        self.axiom, self.angle, self.init_dir, self.rules, self.is_tree = "", 0, 0, {}, False
        self.load_preset()

    def load_preset(self, event=None):
        p = PRESETS[self.preset_var.get()]
        self.axiom, self.angle, self.init_dir, self.rules = p["axiom"], p["angle"], p["dir"], p["rules"]
        self.iter_var.set(p["iter"])
        self.is_tree = p.get("is_tree", False)
        self.draw()

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            header = lines[0].split()
            self.axiom = header[0]
            self.angle = float(header[1])
            self.init_dir = float(header[2])
            self.rules = {}
            for line in lines[1:]:
                if '=' in line:
                    k, v = line.split('=', 1)
                    self.rules[k.strip()] = v.strip()
            self.is_tree = False
            self.draw()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный формат файла:\n{e}")

    def generate_string(self):
        current = self.axiom
        for _ in range(self.iter_var.get()):
            next_str = ""
            for char in current:
                next_str += self.rules.get(char, char)
            current = next_str
        return current

    def interpret(self, cmds):
        x, y = 0.0, 0.0
        d = math.radians(self.init_dir)
        stack = []
        segments = []
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        step = 10.0
        randomness = self.rand_var.get()
        current_depth = 0

        for char in cmds:
            rand_ang = math.radians(random.uniform(-randomness, randomness)) if randomness else 0
            
            if char in ('F', 'G'):
                nx = x + step * math.cos(d + rand_ang)
                ny = y - step * math.sin(d + rand_ang)
                segments.append((x, y, nx, ny, current_depth))
                min_x, min_y = min(min_x, x, nx), min(min_y, y, ny)
                max_x, max_y = max(max_x, x, nx), max(max_y, y, ny)
                x, y = nx, ny
            elif char == 'f':
                x += step * math.cos(d + rand_ang)
                y -= step * math.sin(d + rand_ang)
            elif char == '+': d += math.radians(self.angle) + rand_ang
            elif char == '-': d -= math.radians(self.angle) + rand_ang
            elif char == '[':
                stack.append((x, y, d, current_depth))
                current_depth += 1
            elif char == ']':
                x, y, d, current_depth = stack.pop()
                
        return segments, (min_x, min_y, max_x, max_y)

    def draw(self):
        self.canvas.delete("all")
        cmds = self.generate_string()
        if not cmds: return

        segments, (min_x, min_y, max_x, max_y) = self.interpret(cmds)
        if not segments: return

        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        bbox_w = max_x - min_x if max_x > min_x else 1
        bbox_h = max_y - min_y if max_y > min_y else 1
        
        scale = min(cw / bbox_w, ch / bbox_h) * 0.9
        offset_x = (cw - bbox_w * scale) / 2 - min_x * scale
        offset_y = (ch - bbox_h * scale) / 2 - min_y * scale

        max_depth = max(seg[4] for seg in segments) if self.is_tree else 1

        for x1, y1, x2, y2, depth in segments:
            sx1, sy1 = x1 * scale + offset_x, y1 * scale + offset_y
            sx2, sy2 = x2 * scale + offset_x, y2 * scale + offset_y

            if self.is_tree and max_depth > 0:
                t = depth / max_depth
                # Градиент от коричневого (101, 67, 33) к зеленому (34, 139, 34)
                r = int(101 + t * (34 - 101))
                g = int(67 + t * (139 - 67))
                b = int(33 + t * (34 - 33))
                color = f"#{r:02x}{g:02x}{b:02x}"
                width = max(1, int(8 * (1 - t * 0.8)))
            else:
                color = "black"
                width = 1

            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=width)

if __name__ == "__main__":
    root = tk.Tk()
    app = LSystemApp(root)
    root.mainloop()