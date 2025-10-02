import pygame
import random

class EnemyDebuff(pygame.sprite.Sprite):
    def __init__(self, screen, kind, x, y):
        super().__init__()
        self.screen = screen
        self.kind = kind
        self.image = pygame.image.load(f'images/debuffs/{kind}.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        self.screen.blit(self.image, self.rect)
