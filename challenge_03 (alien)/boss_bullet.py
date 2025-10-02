import pygame
from pygame.sprite import Sprite

class BossBullet(Sprite):
    def __init__(self, ai_game, x, y, kind='laser'):
        super().__init__()
        self.screen = ai_game.screen
        self.kind = kind

        # Lasers = thin, fast — Bombs = wide, slower
        if kind == 'laser':
            self.color = (255, 50, 50)
            self.speed = 5.0
            self.rect = pygame.Rect(x, y, 4, 20)
        elif kind == 'bomb':
            self.color = (255, 200, 0)
            self.speed = 2.5
            self.rect = pygame.Rect(x - 12, y, 24, 24)  # wider area

        self.y = float(self.rect.y)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
