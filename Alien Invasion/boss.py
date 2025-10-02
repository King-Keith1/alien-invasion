import pygame
from pygame.sprite import Sprite

class Boss(Sprite):
    """A final boss with high HP and faster movement."""
    
    def __init__(self, ai_game):
        """Initialize the boss with more health and speed."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.image = pygame.image.load('images/boss.bmp')  # Add a boss image
        self.rect = self.image.get_rect()
        
        # Start boss at the top center
        self.rect.midtop = ai_game.screen.get_rect().midtop

        # Movement & health attributes
        self.speed = 2 * ai_game.settings.alien_speed  # Boss moves faster than aliens
        self.health = 100  # Boss HP

    def update(self):
        """Move the boss left and right at a fast pace."""
        self.rect.x += self.speed
        if self.rect.right >= self.screen.get_rect().right or self.rect.left <= 0:
            self.speed = -self.speed  # Change direction

    def draw(self):
        """Draw the boss on the screen."""
        self.screen.blit(self.image, self.rect)
        self.draw_health_bar()

    def draw_health_bar(self):
        """Draw the boss's HP bar above it."""
        bar_width = self.rect.width
        health_ratio = self.health / 100  # Assuming max HP is 100
        bar_height = 10
        health_bar = pygame.Rect(self.rect.left, self.rect.top - 15, bar_width * health_ratio, bar_height)
        outline_rect = pygame.Rect(self.rect.left, self.rect.top - 15, bar_width, bar_height)

        pygame.draw.rect(self.screen, (255, 0, 0), health_bar)  # Red health bar
        pygame.draw.rect(self.screen, (255, 255, 255), outline_rect, 2)  # White outline