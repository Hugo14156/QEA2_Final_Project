import csv
import os
import tkinter as tk
import math
from typing import List, Tuple
import app_model


def load_points(filename: str) -> List[Tuple[float, float]]:
    """Load points from a CSV file."""
    points = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row:
                points.append((float(row[0]), float(row[1])))
    return points


class FourierVisualizer:
    def __init__(
        self,
        original_pts: List[Tuple[float, float]],
        coeffs: List[Tuple[float, float, float]],
    ):
        self.original_pts = original_pts
        self.all_coeffs = coeffs

        self.root = tk.Tk()
        self.root.title("QEA2 Fourier Reconstruction - Realtime Filtering")

        # UI Layout
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack(padx=20, pady=10)

        # Slider for number of coefficients
        self.slider_label = tk.Label(
            self.root,
            text="Number of Coefficients (Frequency Components):",
            font=("Arial", 10),
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
            command=self.update_plot,  # Call update whenever slider moves
        )
        self.slider.pack(pady=10)

        # Animation Controls
        self.is_animating = False
        self.btn_text = tk.StringVar(value="Play Animation")
        self.play_btn = tk.Button(
            self.root, textvariable=self.btn_text, command=self.toggle_animation
        )
        self.play_btn.pack(pady=10)

        # Initial draw
        self.draw_background()
        self.update_plot()

        print("Visualizer started. Use the slider or 'Play' button.")
        self.root.mainloop()

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

        # Increment and loop back if we hit the end
        next_val = current + 2 if current < max_val else 1
        self.num_coeffs_var.set(next_val)
        self.update_plot()

        # Schedule next frame (50ms delay)
        self.root.after(50, self.animate_step)

    def draw_background(self):
        """Draw the original gray points once."""
        for x, y in self.original_pts:
            self.canvas.create_oval(
                x - 1, y - 1, x + 1, y + 1, fill="#F0F0F0", outline="#F0F0F0", tags="bg"
            )

    def update_plot(self, event=None):
        """Reconstruct and redraw the path based on the current slider value."""
        # Remove old red path
        self.canvas.delete("path")

        n = self.num_coeffs_var.get()
        subset = self.all_coeffs[:n]
        num_points = 1000

        # Use the function from app_model
        points = app_model.get_points_from_coeffs(subset, num_points)

        # Draw path
        if len(points) > 1:
            for i in range(len(points) - 1):
                p1, p2 = points[i], points[i + 1]
                self.canvas.create_line(
                    p1[0], p1[1], p2[0], p2[1], fill="red", width=2, tags="path"
                )


if __name__ == "__main__":
    try:
        pts = load_points("test_drawing_data.csv")
        print(f"Computing full DFT for {len(pts)} points...")
        coeffs = app_model.compute_fourier_coefficients(pts)
        FourierVisualizer(pts, coeffs)
    except Exception as e:
        print(f"Error: {e}")
