import pygame


class Button:
    def __init__(self, rect, text, base_color, hover_color, text_color, action=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action if action is not None else text
        self.is_hovered = False
        self.button_font = pygame.font.SysFont(None, 25)

    def set_text(self, text):
        self.text = text

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.base_color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)

        label = self.button_font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)
