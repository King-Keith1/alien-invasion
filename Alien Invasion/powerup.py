import pygame
import random

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, ai_game, kind):
        super().__init__()
        self.screen = ai_game.screen
        self.kind = kind
        self.settings = ai_game.settings

        self.image = pygame.image.load(f'images/powerups/{kind}.png')
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, self.settings.screen_width - 50)
        self.rect.y = 0

        self.speed = 2

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        self.screen.blit(self.image, self.rect)
