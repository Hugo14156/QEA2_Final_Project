import json
import os
import math

import pygame

from app.model import app_model
from file_types.file_types import ConvertedPoints

MOUSEMOTION = 1024
MOUSEBUTTONDOWN = 1025
MOUSEBUTTONUP = 1026


class Controller:

    def __init__(self):
        self.buttons = []
        self.buttons_by_action = {}
        self.sliders = []
        self.sliders_by_action = {}
        self.canvas = None
        self.toolbar_height = 0
        self.current_mode = "freehand"
        self.eraser_active = False
        self.point_resolution = 100
        self.wave_count = 100
        self.drawing = False
        self.last_pos = None
        self.line_start = None
        self.background_color = (255, 255, 255)
        self.draw_color = (0, 0, 0)
        self.eraser_radius = 12
        self.save_path = os.path.join("saved_series", "drawing.png")
        self.points_path = os.path.join("saved_series", "drawing_points.json")
        self.convert_path = os.path.join("saved_series", "converted_points.json")
        self.drawn_points = []
        self.coeffs = []
        self.convert_requested = False
        self.animation_active = False
        self.animation_paused = False
        self.animation_t = 0.0
        self.animation_speed_control = 25
        self.animation_speed = 0.0025
        self.animation_trace = []
        self.animation_base_surface = None
        self.quit_requested = False

    def set_canvas(self, canvas, toolbar_height):
        self.canvas = canvas
        self.toolbar_height = toolbar_height

    def add_button(self, new_button):
        self.buttons.append(new_button)
        self.buttons_by_action[new_button.action] = new_button

    def add_slider(self, new_slider):
        self.sliders.append(new_slider)
        self.sliders_by_action[new_slider.action] = new_slider
        self._apply_slider_value(new_slider)

    def _apply_slider_value(self, slider):
        if slider.action == "point_resolution":
            self.point_resolution = slider.value
        elif slider.action == "wave_count":
            self.wave_count = slider.value
        elif slider.action == "animation_speed":
            self.animation_speed_control = slider.value
            self.animation_speed = max(0.0001, slider.value / 10000.0)

    def _point_in_canvas(self, point):
        if self.canvas is None:
            return False

        return point[1] >= self.toolbar_height and self.canvas.get_rect().collidepoint(
            point
        )

    def _button_at(self, point):
        for button in self.buttons:
            if button.update(point):
                return button

        return None

    def _current_draw_color(self):
        if self.eraser_active:
            return self.background_color

        return self.draw_color

    def _current_stroke_size(self):
        if self.eraser_active:
            return self.eraser_radius

        return 1

    def _append_drawn_point(self, point):
        point = (int(point[0]), int(point[1]))
        if not self.drawn_points or self.drawn_points[-1] != point:
            self.drawn_points.append(point)

    def _points_between(self, start_pos, end_pos):
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        distance = max(abs(end_x - start_x), abs(end_y - start_y))

        if distance == 0:
            return [(int(start_x), int(start_y))]

        points = []
        for step in range(distance + 1):
            ratio = step / distance
            point = (
                int(round(start_x + (end_x - start_x) * ratio)),
                int(round(start_y + (end_y - start_y) * ratio)),
            )
            if not points or points[-1] != point:
                points.append(point)

        return points

    def _record_segment(self, start_pos, end_pos):
        for point in self._points_between(start_pos, end_pos):
            self._append_drawn_point(point)

    def _sample_drawn_points(self, sample_percent):
        if not self.drawn_points:
            return []

        target_count = max(1, int(round(len(self.drawn_points) * sample_percent / 100)))
        if target_count >= len(self.drawn_points):
            return list(self.drawn_points)

        if target_count == 1:
            return [self.drawn_points[0]]

        cumulative_distances = [0.0]
        total_distance = 0.0
        for index in range(1, len(self.drawn_points)):
            previous_point = self.drawn_points[index - 1]
            current_point = self.drawn_points[index]
            segment_length = math.dist(previous_point, current_point)
            total_distance += segment_length
            cumulative_distances.append(total_distance)

        if total_distance == 0:
            return [self.drawn_points[0]]

        sampled_points = []
        step_distance = total_distance / (target_count - 1)
        for sample_index in range(target_count):
            target_distance = min(total_distance, step_distance * sample_index)
            for segment_index in range(1, len(cumulative_distances)):
                segment_start_distance = cumulative_distances[segment_index - 1]
                segment_end_distance = cumulative_distances[segment_index]

                if (
                    target_distance <= segment_end_distance
                    or segment_index == len(cumulative_distances) - 1
                ):
                    segment_length = segment_end_distance - segment_start_distance
                    if segment_length == 0:
                        sampled_points.append(self.drawn_points[segment_index])
                    else:
                        ratio = (
                            target_distance - segment_start_distance
                        ) / segment_length
                        start_x, start_y = self.drawn_points[segment_index - 1]
                        end_x, end_y = self.drawn_points[segment_index]
                        sampled_points.append(
                            (
                                int(round(start_x + (end_x - start_x) * ratio)),
                                int(round(start_y + (end_y - start_y) * ratio)),
                            )
                        )
                    break

        return sampled_points

    def _save_json(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, indent=2)

    def _draw_point(self, point):
        if self.canvas is None or not self._point_in_canvas(point):
            return

        self._append_drawn_point(point)
        stroke_size = self._current_stroke_size()
        if stroke_size <= 1:
            self.canvas.set_at(point, self._current_draw_color())
            return

        pygame.draw.circle(self.canvas, self._current_draw_color(), point, stroke_size)

    def _draw_line(self, start_pos, end_pos):
        if self.canvas is None:
            return

        pygame.draw.line(
            self.canvas,
            self._current_draw_color(),
            start_pos,
            end_pos,
            self._current_stroke_size(),
        )
        self._record_segment(start_pos, end_pos)

    def _sync_button_labels(self):
        toggle_button = self.buttons_by_action.get("toggle_mode")
        if toggle_button is not None:
            toggle_button.set_text(
                "Line Draw" if self.current_mode == "freehand" else "Free Draw"
            )

        eraser_button = self.buttons_by_action.get("eraser")
        if eraser_button is not None:
            eraser_button.set_text(
                "Eraser On" if not self.eraser_active else "Eraser Off"
            )

        animation_button = self.buttons_by_action.get("toggle_animation")
        if animation_button is not None:
            if not self.animation_active:
                animation_button.set_text("Play Anim")
            elif self.animation_paused:
                animation_button.set_text("Resume Anim")
            else:
                animation_button.set_text("Pause Anim")

    def refresh_button_labels(self):
        self._sync_button_labels()

    def refresh_slider_values(self):
        for slider in self.sliders:
            self._apply_slider_value(slider)

    def toggle_draw_mode(self):
        self.current_mode = "line" if self.current_mode == "freehand" else "freehand"
        self._sync_button_labels()

    def toggle_eraser(self):
        self.eraser_active = not self.eraser_active
        self._sync_button_labels()

    def clear_canvas(self):
        if self.canvas is not None:
            self.canvas.fill(self.background_color)
        self.drawing = False
        self.last_pos = None
        self.line_start = None
        self.drawn_points = []
        self.animation_base_surface = None
        self.stop_animation()

    def stop_animation(self):
        self.animation_active = False
        self.animation_paused = False
        self.animation_t = 0.0
        self.animation_trace = []
        self._sync_button_labels()

    def toggle_animation_pause(self):
        if not self.coeffs:
            return

        if not self.animation_active:
            self.animation_active = True
            self.animation_paused = False
        else:
            self.animation_paused = not self.animation_paused

        self._sync_button_labels()

    def advance_animation_time(self):
        if not self.animation_active or self.animation_paused:
            return False

        previous_t = self.animation_t
        self.animation_t = (self.animation_t + self.animation_speed) % 1.0
        return self.animation_t < previous_t

    def save_drawing(self):
        if self.canvas is None:
            return

        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        pygame.image.save(self.canvas, self.save_path)

        self._save_json(
            self.points_path,
            {
                "drawn_points": [list(point) for point in self.drawn_points],
                "point_resolution": self.point_resolution,
                "wave_count": self.wave_count,
            },
        )

    def load_drawing(self):
        if self.canvas is None or not os.path.exists(self.save_path):
            return

        self.stop_animation()
        self.animation_base_surface = None

        loaded_image = pygame.image.load(self.save_path)
        if loaded_image.get_size() != self.canvas.get_size():
            loaded_image = pygame.transform.smoothscale(
                loaded_image, self.canvas.get_size()
            )

        self.canvas.blit(loaded_image, (0, 0))

        if os.path.exists(self.points_path):
            with open(self.points_path, "r", encoding="utf-8") as file_handle:
                loaded_data = json.load(file_handle)

            self.drawn_points = [
                tuple(point) for point in loaded_data.get("drawn_points", [])
            ]

    def convert_mode(self):
        self.convert_requested = True

        sampled_points = self._sample_drawn_points(self.point_resolution)
        self._save_json(
            self.convert_path,
            {
                "point_resolution": self.point_resolution,
                "wave_count": self.wave_count,
                "total_points": len(self.drawn_points),
                "stored_points": len(sampled_points),
                "points": [list(point) for point in sampled_points],
            },
        )

        self.coeffs = app_model.compute_fourier_coefficients(sampled_points)
        if self.canvas is not None:
            self.animation_base_surface = self.canvas.copy()
        else:
            self.animation_base_surface = None
        self.animation_t = 0.0
        self.animation_trace = []
        self.animation_active = bool(self.coeffs)
        self.animation_paused = False
        self._sync_button_labels()

    def calculate_coeffs(self):
        if not os.path.exists(self.convert_path):
            self.coeffs = []
            self.animation_active = False
            self.animation_paused = False
            self.animation_base_surface = None
            return

        converted_points = ConvertedPoints.load_from_file(self.convert_path)
        points = converted_points.points
        self.coeffs = app_model.compute_fourier_coefficients(points)
        if self.canvas is not None:
            self.animation_base_surface = self.canvas.copy()
        else:
            self.animation_base_surface = None
        self.animation_t = 0.0
        self.animation_trace = []
        self.animation_active = bool(self.coeffs)
        self.animation_paused = False
        self._sync_button_labels()

    def handle_button_action(self, action):
        if action == "save":
            self.save_drawing()
        elif action == "load":
            self.load_drawing()
        elif action == "toggle_mode":
            self.toggle_draw_mode()
        elif action == "clear":
            self.clear_canvas()
        elif action == "eraser":
            self.toggle_eraser()
        elif action == "convert":
            self.convert_mode()
        elif action == "toggle_animation":
            self.toggle_animation_pause()
        elif action == "quit":
            self.quit_requested = True
        elif action == "animate_series":
            self.convert_mode()

    def handle_slider_action(self, slider):
        self._apply_slider_value(slider)

    def handle_events(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                button = self._button_at(event.pos)
                if button is not None:
                    self.handle_button_action(button.action)
                    continue

            slider_handled = False
            for slider in self.sliders:
                if slider.update(event):
                    self.handle_slider_action(slider)
                    slider_handled = True

            if slider_handled:
                continue

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if not self._point_in_canvas(event.pos):
                    continue

                self.stop_animation()
                self.animation_base_surface = None

                if self.current_mode == "freehand":
                    self.drawing = True
                    self.last_pos = event.pos
                    self._draw_point(event.pos)
                elif self.current_mode == "line":
                    self.line_start = event.pos
                    self._draw_point(event.pos)

            elif (
                event.type == MOUSEMOTION
                and self.drawing
                and self.current_mode == "freehand"
            ):
                if self.last_pos is not None and self._point_in_canvas(event.pos):
                    self._draw_line(self.last_pos, event.pos)
                    self.last_pos = event.pos

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if self.current_mode == "freehand":
                    self.drawing = False
                    self.last_pos = None
                elif self.current_mode == "line" and self.line_start is not None:
                    if self._point_in_canvas(event.pos):
                        self._draw_line(self.line_start, event.pos)
                    self.line_start = None
