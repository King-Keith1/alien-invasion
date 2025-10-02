import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, ai_game):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # ✅ Load all ship images correctly:
        self.normal_image = pygame.image.load('images/ship.png')           # ← Changed to PNG

        # ✅ Set starting image:
        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.screen_rect.midbottom

        # Position and movement:
        self.x = float(self.rect.x)
        self.moving_right = False
        self.moving_left = False
        self.speed_factor = self.settings.ship_speed

        # Powerup & debuff flags:
        self.invincible = False
        self.shield_timer = 0

        self.machine_gun = False
        self.gun_timer = 0

        self.double_shot = False
        self.double_timer = 0

        self.fire_locked = False
        self.fire_timer = 0

        self.locked = False
        self.lock_timer = 0

        self.slow_timer = 0

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update the ship's position based on movement flags."""
        if not self.locked:
            if self.moving_right and self.rect.right < self.screen_rect.right:
                self.x += self.speed_factor
            if self.moving_left and self.rect.left > 0:
                self.x -= self.speed_factor
        self.rect.x = self.x

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
