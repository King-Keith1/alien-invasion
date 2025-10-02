import pygame
from pygame.sprite import Sprite
import math

class Bullet(Sprite):
    def __init__(self, ai_game, angle=0):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angle = angle
        self.speed = self.settings.bullet_speed

    def update(self):
        rad = math.radians(self.angle)
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
