import pygame

MOUSEBUTTONDOWN = 1025
MOUSEBUTTONUP = 1026
MOUSEMOTION = 1024


class Slider:
    def __init__(self, rect, label, min_value, max_value, value, action=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.action = action if action is not None else label.lower().replace(" ", "_")
        self.is_dragging = False
        self.font = pygame.font.SysFont(None, 24)

    def clamp_value(self, value):
        return max(self.min_value, min(self.max_value, value))

    def set_value(self, value):
        self.value = self.clamp_value(value)

    def get_handle_x(self):
        if self.max_value == self.min_value:
            return self.rect.x

        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return int(self.rect.x + ratio * self.rect.width)

    def _set_value_from_mouse(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        ratio = relative_x / self.rect.width if self.rect.width else 0
        self.value = int(
            round(self.min_value + ratio * (self.max_value - self.min_value))
        )

    def update(self, event):
        if (
            event.type == MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.is_dragging = True
            self._set_value_from_mouse(event.pos[0])
            return True

        if event.type == MOUSEMOTION and self.is_dragging:
            self._set_value_from_mouse(event.pos[0])
            return True

        if event.type == MOUSEBUTTONUP and event.button == 1 and self.is_dragging:
            self.is_dragging = False
            return True

        return False

    def draw(self, screen):
        label_surface = self.font.render(
            f"{self.label}: {self.value_display()}", True, (240, 240, 240)
        )
        screen.blit(label_surface, (self.rect.x, self.rect.y - 24))

        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(screen, (110, 110, 110), track_rect, border_radius=3)

        handle_x = self.get_handle_x()
        handle_rect = pygame.Rect(0, 0, 18, 18)
        handle_rect.center = (handle_x, self.rect.centery)
        pygame.draw.circle(screen, (235, 235, 235), handle_rect.center, 9)
        pygame.draw.circle(screen, (80, 120, 200), handle_rect.center, 9, 2)

    def value_display(self):
        if self.max_value == 100 and self.min_value == 20:
            return f"{self.value}%"

        return str(self.value)
