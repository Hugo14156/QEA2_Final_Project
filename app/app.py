import pygame
import tkinter as tk

from app.control import Controller

# from app.model.model import Model
from app.view.view import View


class App:

    def __init__(self):
        self.controller = Controller()
        self.view = View(self.controller)

    def run_app(self):
        init_function = getattr(pygame, "init")
        init_function()
        clock = pygame.time.Clock()
        running = True
        screen = pygame.display.set_mode(self.get_display_resolution())
        self.view.set_screen(screen)
        self.controller.set_canvas(self.view.get_canvas(), self.view.toolbar_height)
        self.view.add_button(
            (20, 30, 90, 42),
            "Save",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="save",
        )
        self.view.add_button(
            (120, 30, 90, 42),
            "Load",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="load",
        )
        self.view.add_button(
            (220, 30, 120, 42),
            "Line Draw",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="toggle_mode",
        )
        self.view.add_button(
            (350, 30, 90, 42),
            "Clear",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="clear",
        )
        self.view.add_button(
            (450, 30, 100, 42),
            "Eraser On",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="eraser",
        )
        self.view.add_button(
            (560, 30, 110, 42),
            "Convert",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="convert",
        )
        self.controller.refresh_button_labels()
        self.view.add_slider(
            (20, 125, 320, 24),
            "Point Resolution",
            20,
            100,
            100,
            action="point_resolution",
        )
        self.view.add_slider(
            (380, 125, 320, 24),
            "Wave Count",
            10,
            500,
            100,
            action="wave_count",
        )
        self.controller.refresh_slider_values()

        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == 256:
                    running = False
                    break

            self.controller.handle_events(events)

            self.view.draw()

            # flip() the display to put your work on screen
            pygame.display.flip()

            clock.tick(60)  # limits FPS to 60

        quit_function = getattr(pygame, "quit")
        quit_function()

    def get_display_resolution(self):
        root = tk.Tk()
        root.withdraw()
        return (root.winfo_screenwidth(), root.winfo_screenheight())
