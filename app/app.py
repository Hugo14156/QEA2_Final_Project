import pygame

from app.control import Controller
from app.view.view import View


class App:

    def __init__(self):
        self.controller = Controller()
        self.view = View(self.controller)
        self.fourier_coefficients = ()

    def run_app(self):
        pygame.init()
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
        self.view.add_button(
            (680, 30, 130, 42),
            "Play Anim",
            (90, 110, 160),
            (120, 145, 210),
            (255, 255, 255),
            action="toggle_animation",
        )
        self.view.add_button(
            (820, 30, 90, 42),
            "Quit",
            (150, 70, 70),
            (180, 90, 90),
            (255, 255, 255),
            action="quit",
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
            5000,
            100,
            action="wave_count",
        )
        self.view.add_slider(
            (740, 125, 260, 24),
            "Anim Speed",
            5,
            200,
            self.controller.animation_speed_control,
            action="animation_speed",
        )
        self.controller.refresh_slider_values()

        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break

            self.controller.handle_events(events)

            if self.controller.quit_requested:
                running = False
                continue

            if self.controller.animation_active:
                if self.controller.animation_base_surface is not None:
                    self.view.get_canvas().blit(
                        self.controller.animation_base_surface, (0, 0)
                    )
                else:
                    self.view.clear_canvas()
                endpoint = self.view.animate_coeffs(
                    self.controller.coeffs,
                    min(self.controller.wave_count, len(self.controller.coeffs)),
                    self.controller.animation_t,
                )

                if endpoint is not None and not self.controller.animation_paused:
                    self.controller.animation_trace.append(endpoint)

                self.view.draw_trace(self.controller.animation_trace)

                if self.controller.advance_animation_time():
                    self.controller.animation_trace = []

            self.view.draw()

            # flip() the display to put your work on screen
            pygame.display.flip()

            clock.tick(60)  # limits FPS to 60

        pygame.quit()

    def get_display_resolution(self):
        info = pygame.display.Info()
        return (info.current_w, info.current_h)
