import tkinter as tk
from tkinter import messagebox
import math
from typing import List, Tuple, Optional


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class BezierCurveApp:   
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Кубические сплайны Безье")
        self.root.geometry("960x540")
        
        self.control_points: List[Point] = []
        
        self.dragging_point: Optional[int] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        self.point_radius = 4
        self.curve_color = "black"
        self.point_color = "green"
        self.selected_point_color = "red"
        
        self._build_ui()
    
    def _build_ui(self):
        """Создание интерфейса."""
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        btn_clear = tk.Button(control_frame, text="Очистить", 
                              command=self._clear_points, bg="#ff6666")
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        btn_help = tk.Button(control_frame, text="Справка", 
                             command=self._show_help)
        btn_help.pack(side=tk.LEFT, padx=5)
        
        info_frame = tk.Frame(self.root, padx=10, pady=5, bg="#f0f0f0")
        info_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.info_label = tk.Label(info_frame, 
                                   text="Количество точек: 0",
                                   bg="#f0f0f0", font=("Arial", 10))
        self.info_label.pack(side=tk.LEFT)
        
        self.canvas = tk.Canvas(self.root, bg="white", 
                                highlightthickness=2, highlightbackground="#333")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._on_right_click)
        
        self._redraw()
    
    def _clear_points(self):
        self.control_points.clear()
        self._redraw()
    
    def _show_help(self):
        help_text = """
Управление составной кубической кривой Безье:

• ЛКМ на пустом месте — добавить точку
• ЛКМ на точке + перетаскивание — переместить точку
• ПКМ на точке — удалить точку
        """
        messagebox.showinfo("Справка", help_text)
    
    def _on_left_click(self, event):
        click_point = Point(event.x, event.y)
        
        for i, point in enumerate(self.control_points):
            if point.distance_to(click_point) < self.point_radius * 2:
                self.dragging_point = i
                self.drag_offset_x = event.x - point.x
                self.drag_offset_y = event.y - point.y
                return
        
        self.control_points.append(click_point)
        self._redraw()
    
    def _on_drag(self, event):
        if self.dragging_point is not None:
            self.control_points[self.dragging_point].x = event.x - self.drag_offset_x
            self.control_points[self.dragging_point].y = event.y - self.drag_offset_y
            self._redraw()
    
    def _on_release(self, event):
        self.dragging_point = None
    
    def _on_right_click(self, event):
        click_point = Point(event.x, event.y)
        
        for i, point in enumerate(self.control_points):
            if point.distance_to(click_point) < self.point_radius * 2:
                self.control_points.pop(i)
                self._redraw()
                return
    
    def _compute_bezier_points(self, t: float, p0: Point, p1: Point, 
                                p2: Point, p3: Point) -> Point:
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t
        
        x = (p0.x * mt3 + 
             3 * p1.x * mt2 * t + 
             3 * p2.x * mt * t2 + 
             p3.x * t3)
        
        y = (p0.y * mt3 + 
             3 * p1.y * mt2 * t + 
             3 * p2.y * mt * t2 + 
             p3.y * t3)
        
        return Point(x, y)
    
    def _compute_catmull_rom_to_bezier(self, p0: Point, p1: Point, 
                                        p2: Point, p3: Point) -> Tuple[Point, Point]:
        b1 = Point(
            p1.x + (p2.x - p0.x) / 6,
            p1.y + (p2.y - p0.y) / 6
        )
        
        b2 = Point(
            p2.x - (p3.x - p1.x) / 6,
            p2.y - (p3.y - p1.y) / 6
        )
        
        return b1, b2
    
    def _get_bezier_segments(self) -> List[Tuple[Point, Point, Point, Point]]:
        if len(self.control_points) < 2:
            return []
        
        segments = []
        n = len(self.control_points)
        
        for i in range(n - 1):           
            if i == 0:
                p0 = Point(2 * self.control_points[0].x - self.control_points[1].x,
                          2 * self.control_points[0].y - self.control_points[1].y)
                p1 = self.control_points[0]
                p2 = self.control_points[1]
                p3 = self.control_points[2] if n > 2 else Point(2 * p2.x - p1.x,
                                                                 2 * p2.y - p1.y)
            elif i == n - 2:
                p0 = self.control_points[i - 1]
                p1 = self.control_points[i]
                p2 = self.control_points[i + 1]
                p3 = Point(2 * p2.x - p1.x, 2 * p2.y - p1.y)
            else:
                p0 = self.control_points[i - 1]
                p1 = self.control_points[i]
                p2 = self.control_points[i + 1]
                p3 = self.control_points[i + 2]
            
            b1, b2 = self._compute_catmull_rom_to_bezier(p0, p1, p2, p3)
            
            segments.append((p1, b1, b2, p2))
        
        return segments
    
    def _redraw(self):
        self.canvas.delete("all")
        
        segments = self._get_bezier_segments()
        
        if segments:
            all_curve_points = []
            
            for seg_idx, (p0, p1, p2, p3) in enumerate(segments):
                num_steps = 100
                for i in range(num_steps + 1):
                    t = i / num_steps
                    point = self._compute_bezier_points(t, p0, p1, p2, p3)
                    all_curve_points.append(point)
            
            if len(all_curve_points) > 1:
                coords = []
                for point in all_curve_points:
                    coords.extend([point.x, point.y])
                self.canvas.create_line(coords, fill=self.curve_color, 
                                       width=2, smooth=True)
        
        for i, point in enumerate(self.control_points):
            color = self.selected_point_color if i == self.dragging_point else self.point_color
            self.canvas.create_oval(
                point.x - self.point_radius, 
                point.y - self.point_radius,
                point.x + self.point_radius, 
                point.y + self.point_radius,
                fill=color,
            )
        
        self.info_label.config(
            text=f"Количество точек: {len(self.control_points)}"
        )


def main():
    root = tk.Tk()
    app = BezierCurveApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
