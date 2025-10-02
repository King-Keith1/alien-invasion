import pygame
from pygame.sprite import Sprite

class AlienBullet(Sprite):
    def __init__(self, ai_game, x, y):
        super().__init__()
        self.screen = ai_game.screen
        self.color = (255, 50, 50)
        self.rect = pygame.Rect(x, y, 3, 16)
        self.y = float(self.rect.y)
        self.speed = 2.5  # You can increase this for harder bullets

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
