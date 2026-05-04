import pygame
import math

from app.view.button import Button
from app.view.slider import Slider


class View:

    def __init__(self, controller, screen=None):
        if screen is not None:
            self.set_screen(screen)
        else:
            self._window_width = None
            self._window_height = None
            self.screen = screen
            self.canvas = None
        self.toolbar_height = 170
        self.canvas_background = (255, 255, 255)
        self.buttons = []
        self.sliders = []
        self.controller = controller

    def set_screen(self, new_screen):
        self.screen = new_screen
        self._window_width = new_screen.get_width()
        self._window_height = new_screen.get_height()
        self.canvas = pygame.Surface((self._window_width, self._window_height))
        self.canvas.fill(self.canvas_background)

    def clear_canvas(self):
        if self.canvas is not None:
            self.canvas.fill(self.canvas_background)

    def draw(self):
        if self.screen is None or self.canvas is None:
            return

        self.screen.blit(self.canvas, (0, 0))
        toolbar_color = (42, 42, 42)
        pygame.draw.rect(
            self.screen, toolbar_color, (0, 0, self._window_width, self.toolbar_height)
        )

        for button in self.buttons:
            button.draw(self.screen)

        for slider in self.sliders:
            slider.draw(self.screen)

        status_font = pygame.font.SysFont(None, 28)
        mode_label = f"Mode: {self.controller.current_mode}"
        if self.controller.eraser_active:
            mode_label += " | Eraser on"
        mode_label += f" | Point Resolution: {self.controller.point_resolution}%"
        mode_label += f" | Wave Count: {self.controller.wave_count}"
        if self.controller.animation_active:
            animation_state = (
                "Paused" if self.controller.animation_paused else "Playing"
            )
        else:
            animation_state = "Stopped"
        mode_label += f" | Animation: {animation_state}"
        mode_label += f" | Anim Speed: {self.controller.animation_speed_control}"
        status_surface = status_font.render(mode_label, True, (240, 240, 240))
        self.screen.blit(status_surface, (16, self.toolbar_height - 34))

    def add_button(self, rect, text, base_color, hover_color, text_color, action=None):
        new_button = Button(
            rect, text, base_color, hover_color, text_color, action=action
        )
        self.buttons.append(new_button)
        self.controller.add_button(new_button)

    def add_slider(self, rect, label, min_value, max_value, value, action=None):
        new_slider = Slider(rect, label, min_value, max_value, value, action=action)
        self.sliders.append(new_slider)
        self.controller.add_slider(new_slider)

    def draw_trace(self, points):
        if self.canvas is None or len(points) < 2:
            return

        pygame.draw.lines(
            self.canvas,
            (220, 70, 70),
            False,
            [(int(round(x)), int(round(y))) for x, y in points],
            2,
        )

    def animate_coeffs(self, coeffs, coeff_count, t):
        if self.canvas is None or coeffs is None:
            return None

        try:
            coeff_count = max(0, int(coeff_count))
        except (TypeError, ValueError):
            return None

        active_coeffs = list(coeffs[:coeff_count])
        if not active_coeffs:
            return None

        # Keep t in [0, 1) and map one loop to 2*pi radians.
        time_angle = 2.0 * math.pi * (float(t) % 1.0)

        current_x = 0.0
        current_y = 0.0

        circle_color = (140, 140, 140)
        arm_color = (70, 150, 245)
        tip_color = (255, 90, 70)

        for freq, amplitude, phase in active_coeffs:
            radius = float(amplitude)
            angle = float(freq) * time_angle + float(phase)

            next_x = current_x + radius * math.cos(angle)
            next_y = current_y + radius * math.sin(angle)

            if radius > 0.0:
                pygame.draw.circle(
                    self.canvas,
                    circle_color,
                    (int(round(current_x)), int(round(current_y))),
                    int(round(radius)),
                    1,
                )

            pygame.draw.line(
                self.canvas,
                arm_color,
                (int(round(current_x)), int(round(current_y))),
                (int(round(next_x)), int(round(next_y))),
                2,
            )

            current_x, current_y = next_x, next_y

        pygame.draw.circle(
            self.canvas,
            tip_color,
            (int(round(current_x)), int(round(current_y))),
            3,
        )

        return (current_x, current_y)

    def get_canvas(self):
        return self.canvas
