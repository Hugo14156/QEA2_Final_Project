import pygame

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

    def get_canvas(self):
        return self.canvas
