from vec2 import vec2
import pygame
from Text import Text


class Button:
    def __init__(self, button_size: vec2, button_pos: vec2, text: str, text_color, font_name: str, button_color, font_size):
        self.size = button_size
        self.button_pos = button_pos
        self.button_color = button_color
        self.message = text
        self.font_size = font_size
        self.font_name = font_name
        self.text_color = text_color
        self.text_pos = self.button_pos
        self.button_text = Text(pos=self.text_pos, text=self.message, font_name=font_name, font_size=self.font_size, color=self.text_color)
        self.button = pygame.Rect((self.button_pos.x, self.button_pos.y), (self.size.x, self.size.y))
        self.on = False
        self.button_center_pos = vec2(self.button_pos.x + self.size.x/2, self.button_pos.y + self.size.y/2)

    def draw_button(self, screen):
        pygame.draw.rect(screen, self.button_color, self.button)
        self.button_text.draw()

    def center_at(self, size):
        self.button_pos = vec2(size[0] / 2 - self.size.x / 2, size[1] / 2 - self.size.y / 2)
        self.text_pos = self.button_center_pos.x - self.button_text.surface.get_width()
