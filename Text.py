from vec2 import vec2
import pygame


class Text:
    def __init__(self, pos: vec2, text: str, font_name: str, font_size: int, color):
        self.pos = pos
        self.font_size = font_size
        self.font = font_name
        self.text = text
        self.font = pygame.font.SysFont(self.font, self.font_size)
        self.color = color
        self.surface = self.font.render(self.text, True, self.color)
        self.width = self.surface.get_width()
        self.height = font_size

    def draw(self):
        self.surface = self.font.render(self.text, True, self.color)
        pygame.display.get_surface().blit(self.surface, (self.pos.x, self.pos.y))
