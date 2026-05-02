import os
import sys
import tkinter as tk
from typing import List, Tuple

# Ensure the necessary directories are in sys.path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
file_types_dir = os.path.join(project_root, "file_types")

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if file_types_dir not in sys.path:
    sys.path.insert(0, file_types_dir)

import app_model
from file_types import ConvertedPoints

"""
This file is a simple test to render Fourier data.
It includes a zoom-to-fit visualizer and a scrollable amplitude list.
"""


class FourierVisualizer:
    def __init__(
        self,
        original_pts: List[Tuple[float, float]],
        coeffs: List[Tuple[float, float, float]],
    ):
        self.original_pts = original_pts
        self.all_coeffs = coeffs

        # Calculate bounding box for zoom-to-fit
        if original_pts:
            xs = [p[0] for p in original_pts]
            ys = [p[1] for p in original_pts]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            draw_w = max_x - min_x
            draw_h = max_y - min_y
            draw_w = max(1, draw_w)
            draw_h = max(1, draw_h)

            canvas_w, canvas_h = 800, 500
            padding = 40

            scale_x = (canvas_w - 2 * padding) / draw_w
            scale_y = (canvas_h - 2 * padding) / draw_h
            self.scale = min(scale_x, scale_y)

            self.offset_x = (canvas_w - draw_w * self.scale) / 2 - min_x * self.scale
            self.offset_y = (canvas_h - draw_h * self.scale) / 2 - min_y * self.scale
        else:
            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0

        self.root = tk.Tk()
        self.root.title("QEA2 Fourier Reconstruction - Zoom to Fit")

        # Main Drawing Canvas
        self.canvas = tk.Canvas(self.root, width=800, height=500, bg="white")
        self.canvas.pack(padx=20, pady=10)

        # Reconstruction Slider
        self.slider_label = tk.Label(
            self.root,
            text="Number of Coefficients (Frequency Components):",
            font=("Arial", 10, "bold"),
        )
        self.slider_label.pack()

        self.num_coeffs_var = tk.IntVar(value=min(len(coeffs), 50))
        self.slider = tk.Scale(
            self.root,
            from_=1,
            to=len(coeffs),
            orient="horizontal",
            length=600,
            variable=self.num_coeffs_var,
            command=self.update_plot,
        )
        self.slider.pack(pady=5)

        # Amplitude List UI
        self.amp_label = tk.Label(
            self.root,
            text="Amplitude Distribution (Freq: Amplitude):",
            font=("Arial", 10, "bold"),
        )
        self.amp_label.pack(pady=(10, 0))

        self.amp_canvas = tk.Canvas(self.root, width=750, height=60, bg="#F0F0F0")
        self.amp_canvas.pack(padx=20, pady=5)

        self.amp_scroll_var = tk.IntVar(value=0)
        self.amp_slider = tk.Scale(
            self.root,
            from_=0,
            to=max(0, len(coeffs) - 10),
            orient="horizontal",
            length=600,
            showvalue=False,
            variable=self.amp_scroll_var,
            command=self.draw_amplitudes,
        )
        self.amp_slider.pack(pady=5)

        # Play/Stop Button
        self.is_animating = False
        self.btn_text = tk.StringVar(value="Play Animation")
        self.play_btn = tk.Button(
            self.root, textvariable=self.btn_text, command=self.toggle_animation
        )
        self.play_btn.pack(pady=10)

        # Initial draw
        self.draw_background()
        self.update_plot()
        self.draw_amplitudes()

        self.root.mainloop()

    def transform_pt(self, x, y):
        return x * self.scale + self.offset_x, y * self.scale + self.offset_y

    def toggle_animation(self):
        self.is_animating = not self.is_animating
        if self.is_animating:
            self.btn_text.set("Stop Animation")
            self.animate_step()
        else:
            self.btn_text.set("Play Animation")

    def animate_step(self):
        if not self.is_animating:
            return
        current = self.num_coeffs_var.get()
        max_val = len(self.all_coeffs)
        next_val = current + 2 if current < max_val else 1
        self.num_coeffs_var.set(next_val)
        self.update_plot()
        self.root.after(50, self.animate_step)

    def draw_background(self):
        for x, y in self.original_pts:
            tx, ty = self.transform_pt(x, y)
            self.canvas.create_oval(
                tx - 1,
                ty - 1,
                tx + 1,
                ty + 1,
                fill="#E0E0E0",
                outline="#E0E0E0",
                tags="bg",
            )

    def draw_amplitudes(self, event=None):
        self.amp_canvas.delete("all")

        # Sort amplitude by frequency
        sorted_coeffs = sorted(self.all_coeffs, key=lambda x: x[0])

        start_idx = self.amp_scroll_var.get()
        max_amp = max([c[1] for c in sorted_coeffs]) if sorted_coeffs else 1

        item_width = 75
        for i in range(11):
            idx = start_idx + i
            if idx >= len(sorted_coeffs):
                break

            freq, amp, _ = sorted_coeffs[idx]

            # Color calculation: larger is darker
            intensity = int(255 * (1 - (amp / max_amp)))
            color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
            text_color = "white" if intensity < 120 else "black"

            x_pos = i * item_width
            self.amp_canvas.create_rectangle(
                x_pos, 0, x_pos + item_width, 60, fill=color, outline="#CCCCCC"
            )
            self.amp_canvas.create_text(
                x_pos + item_width / 2,
                30,
                text=f"F: {int(freq)}\nA: {amp:.1f}",
                fill=text_color,
                font=("Arial", 8, "bold"),
                justify="center",
            )

    def update_plot(self, event=None):
        self.canvas.delete("path")
        n = self.num_coeffs_var.get()
        subset = self.all_coeffs[:n]
        points = app_model.get_points_from_coeffs(subset, 10000)

        if len(points) > 1:
            transformed_points = [self.transform_pt(px, py) for px, py in points]
            for i in range(len(transformed_points) - 1):
                p1, p2 = transformed_points[i], transformed_points[i + 1]
                self.canvas.create_line(
                    p1[0], p1[1], p2[0], p2[1], fill="red", width=2, tags="path"
                )

            self.canvas.create_line(
                transformed_points[-1][0],
                transformed_points[-1][1],
                transformed_points[0][0],
                transformed_points[0][1],
                fill="red",
                width=2,
                tags="path",
            )


if __name__ == "__main__":
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(
            script_dir, "..", "..", "saved_series", "converted_points.json"
        )

        cp = ConvertedPoints.load_from_file(json_path)
        pts = cp.points

        print(f"Computing full DFT for {len(pts)} points...")
        coeffs = app_model.compute_fourier_coefficients(pts)

        FourierVisualizer(pts, coeffs)
    except Exception as e:
        print(f"Error: {e}")
