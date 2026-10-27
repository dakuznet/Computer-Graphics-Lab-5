import tkinter as tk
import random


def midpoint_step(points, roughness, rng):
    result = [points[0]]
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        length = x2 - x1
        xm = (x1 + x2) / 2
        ym = (y1 + y2) / 2 + rng.uniform(-1, 1) * roughness * length
        result.append((xm, ym))
        result.append((x2, y2))
    return result


def build_steps(h_left, h_right, roughness, steps, seed):
    rng = random.Random(seed)
    steps_list = [[(0.0, h_left), (1.0, h_right)]]
    for _ in range(steps):
        steps_list.append(midpoint_step(steps_list[-1], roughness, rng))
    return steps_list


class MidpointDisplacementApp:
    MARGIN = 30

    def __init__(self, root):
        self.root = root
        self.root.title("Midpoint displacement")
        self.root.geometry("1000x600")

        self.roughness = tk.DoubleVar(value=0.5)
        self.steps = tk.IntVar(value=8)
        self.h_left = tk.DoubleVar(value=0.3)
        self.h_right = tk.DoubleVar(value=0.5)
        self.seed = random.randint(0, 99999)

        self.steps_list = []
        self.current_step = 0

        self._build_ui()
        self._regenerate()

    def _build_ui(self):
        panel = tk.Frame(self.root, padx=10, pady=10)
        panel.pack(side=tk.LEFT, fill=tk.Y)

        self._add_scale(panel, "Шероховатость R", self.roughness, 0.0, 1.5, 0.05)
        self._add_scale(panel, "Число шагов", self.steps, 1, 12, 1)
        self._add_scale(panel, "Высота левого края", self.h_left, 0.0, 1.0, 0.05)
        self._add_scale(panel, "Высота правого края", self.h_right, 0.0, 1.0, 0.05)

        tk.Button(panel, text="Сгенерировать заново",
                  command=self._new_seed).pack(fill=tk.X, pady=5)

        nav = tk.Frame(panel)
        nav.pack(fill=tk.X, pady=5)
        tk.Button(nav, text="< Шаг назад",
                  command=lambda: self._set_step(self.current_step - 1)).pack(side=tk.LEFT)
        tk.Button(nav, text="Шаг вперёд >",
                  command=lambda: self._set_step(self.current_step + 1)).pack(side=tk.RIGHT)

        self.info_label = tk.Label(panel, text="")
        self.info_label.pack(anchor="w")

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw())

    def _add_scale(self, parent, label, var, from_, to, resolution):
        tk.Scale(parent, label=label, variable=var, from_=from_, to=to,
                 resolution=resolution, orient=tk.HORIZONTAL, length=220,
                 command=lambda _: self._regenerate()).pack(fill=tk.X)

    def _regenerate(self):
        if not hasattr(self, "canvas"):
            return
        self.steps_list = build_steps(self.h_left.get(), self.h_right.get(),
                                      self.roughness.get(), self.steps.get(), self.seed)
        self.current_step = len(self.steps_list) - 1
        self._redraw()

    def _new_seed(self):
        self.seed = random.randint(0, 99999)
        self._regenerate()

    def _set_step(self, step):
        self.current_step = max(0, min(step, len(self.steps_list) - 1))
        self._redraw()

    def _redraw(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 50 or h < 50 or not self.steps_list:
            return

        ys = [y for step in self.steps_list for _, y in step]
        y_min, y_max = min(ys), max(ys)
        if y_max - y_min < 1e-9:
            y_min, y_max = y_min - 0.5, y_max + 0.5

        m = self.MARGIN
        coords = []
        for x, y in self.steps_list[self.current_step]:
            coords.append(m + x * (w - 2 * m))
            coords.append(h - m - (y - y_min) / (y_max - y_min) * (h - 2 * m))

        c.create_polygon([coords[0], h] + coords + [coords[-2], h],
                         fill="#7d8f69", outline="black", width=2)

        self.info_label.config(
            text=f"Шаг: {self.current_step} из {len(self.steps_list) - 1}")


def main():
    root = tk.Tk()
    app = MidpointDisplacementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()