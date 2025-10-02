import pygame
from pygame.sprite import Sprite

class Boss(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/boss.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (120, 80))  # Resize if needed
        self.rect = self.image.get_rect()
        self.rect.midtop = ai_game.screen.get_rect().midtop

        self.x = float(self.rect.x)
        self.direction = 1
        self.speed = 1.5
        self.health = 100
        self.max_health = 100

    def update(self):
        self.x += self.direction * self.speed
        self.rect.x = self.x

        # Bounce off screen edges
        if self.rect.right >= self.screen.get_width() or self.rect.left <= 0:
            self.direction *= -1

    def draw(self):
        self.screen.blit(self.image, self.rect)
        self._draw_health_bar()

    def _draw_health_bar(self):
        bar_width = self.rect.width
        bar_height = 6
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)

        pygame.draw.rect(self.screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 1)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0  # Clamp