import sys
import random
import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from powerup import PowerUp
from enemy_debuff import EnemyDebuff
from alien_bullet import AlienBullet
from boss import Boss
from boss_bullet import BossBullet


class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        self.bg_image = pygame.image.load('Background.png').convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (self.settings.screen_width, self.settings.screen_height))
        
        pygame.mixer.init()
        pygame.mixer.music.load('sounds/music.mp3')
        pygame.mixer.music.play(-1)  # Loop forever
        pygame.mixer.music.set_volume(0.3)
        
        self.player_laser = pygame.mixer.Sound('sounds/laser.wav')
        self.alien_laser = pygame.mixer.Sound('sounds/laser2.wav')
        self.bomb = pygame.mixer.Sound('sounds/bomb.wav')
        self.boss_death = pygame.mixer.Sound('sounds/boss_death.wav')
        self.boss_laser = pygame.mixer.Sound('sounds/boss_laser.wav')
        self.debuff = pygame.mixer.Sound('sounds/debuff.wav')
        self.nuke = pygame.mixer.Sound('sounds/nuke.wav')
        self.powerup = pygame.mixer.Sound('sounds/powerup.wav')
        self.boss_bomb = pygame.mixer.Sound('sounds/boss_bomb.wav')
        
        self.player_laser.set_volume(0.4)     # Player fire
        self.alien_laser.set_volume(0.3)      # Alien shots (quieter so not annoying)
        self.boss_laser.set_volume(0.6)       # Boss laser = high danger
        self.boss_bomb.set_volume(0.7)        # Boss bomb = even more threat
        self.boss_death.set_volume(0.8)       # Emphasize boss death
        self.powerup.set_volume(0.3)          # Subtle ding
        self.debuff.set_volume(0.4)           # Slight warning buzz
        self.bomb.set_volume(0.6)             # Big hit
        self.nuke.set_volume(0.7)             # BOOM
        
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.debuffs = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.boss_bullets = pygame.sprite.Group()
        self.last_boss_attack = 0
        self.last_shot_time = 0


        self.boss = None


        self.play_button = Button(self, "Play")
        self.game_active = False
        self.last_debuff_time = 0
        self.laser_beam_active = False


        self._create_fleet()

    def run_game(self):
        while True:
            self._check_events()

            if self.laser_beam_active:
                self._check_laser_hits()

            if self.game_active:
                self.ship.update()
                self.bullets.update()
                self._check_fleet_edges()
                self.aliens.update()
                self._maybe_alien_fire()
                self.alien_bullets.update()
                self.powerups.update()
                self.debuffs.update()

                self._check_bullet_collisions()
                self._check_alien_collisions()
                self._check_powerup_collisions()
                self._check_debuff_collisions()
                self._check_powerup_timers()
                self._check_debuff_timers()
                self._maybe_drop_debuff()
                
            if self.game_active:
                self.ship.update()    
                
            if self.boss:
                self.boss.update()
                
            if self.boss:
                self._boss_maybe_attack()
                self.boss_bullets.update()
    
                keys = pygame.key.get_pressed()
                if self.ship.machine_gun and keys[pygame.K_SPACE]:
                    now = pygame.time.get_ticks()
                    if now - self.last_shot_time > 150:
                        self._fire_bullet()
                        self.last_shot_time = now

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.USEREVENT + 1:
                self.ship.image = self.ship.normal_image
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Turn off timer
            elif event.type == pygame.USEREVENT + 2:
                self.ship.image = self.ship.normal_image
                pygame.time.set_timer(pygame.USEREVENT + 2, 0)  # Turn off timer
    
    def _check_keydown_events(self, event):
        if event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            if self.ship.machine_gun:
                self.laser_beam_active = True
            elif not self.ship.fire_locked:
                self._fire_bullet()
        elif event.key == pygame.K_p and not self.game_active:
            self._start_game()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            self.laser_beam_active = False

    def _check_play_button(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos) and not self.game_active:
            self._start_game()

    def _start_game(self):
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True
        pygame.mouse.set_visible(False)

        self.aliens.empty()
        self.bullets.empty()
        self.powerups.empty()
        self.debuffs.empty()

        self._create_fleet()
        self.ship.center_ship()

    def _fire_bullet(self):
        if len(self.bullets) >= self.settings.bullets_allowed or self.ship.fire_locked:
            return

        if self.ship.machine_gun:
            # Shotgun spread — 3 angled bullets
            for angle in [-15, 0, 15]:
                bullet = Bullet(self, angle)
                self.bullets.add(bullet)

        elif self.ship.double_shot:
            # Double shot — 2 parallel bullets
            left = Bullet(self)
            right = Bullet(self)
            left.rect.x -= 10
            right.rect.x += 10
            left.x = float(left.rect.x)
            right.x = float(right.rect.x)
            self.bullets.add(left, right)

        else:
            bullet = Bullet(self)
            self.bullets.add(bullet)

        self.player_laser.play()



    def _check_bullet_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for alien_group in collisions.values():
                for alien in alien_group:
                    self._maybe_drop_powerup(alien)
                    self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()
        
        if self.boss:
            for bullet in self.bullets.copy():
                if bullet.rect.colliderect(self.boss.rect):
                    self.boss.take_damage(10)  # You can adjust damage
                    self.bullets.remove(bullet)

            # If boss is defeated
            if self.boss.health <= 0:
                self.boss = None
                self.stats.level += 1
                self.sb.prep_level()
                self.settings.increase_speed()
                self._create_fleet()    

        if not self.aliens and not self.boss:
            self.bullets.empty()
            self.stats.level += 1
            self.sb.prep_level()
            self.settings.increase_speed()

            if self.stats.level % 5 == 0:
                self.boss = Boss(self)
            else:
                self._create_fleet()

    def _check_alien_collisions(self):
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()
        
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()    
            
        for bullet in self.boss_bullets:
            if self.ship.rect.colliderect(bullet.rect):
                self._ship_hit()
                self.boss_bullets.remove(bullet)
                break    

    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        current_x, current_y = alien_width, alien_height

        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self, x, y):
        new_alien = Alien(self)
        new_alien.x = x
        new_alien.rect.x = x
        new_alien.rect.y = y
        self.aliens.add(new_alien)

    def _maybe_drop_powerup(self, alien):
        chance = random.random()
        if chance < 0.01:
            kind = 'nuke'
        elif chance < 0.05:
            kind = 'bomb'
        elif chance < 0.10:
            kind = 'double'
        elif chance < 0.20:
            kind = 'shield'
        elif self.stats.level >= 2 and chance < 0.40:
            kind = 'machine'
        else:
            return
        powerup = PowerUp(self, kind)
        powerup.rect.center = alien.rect.center
        self.powerups.add(powerup)

    def _maybe_drop_debuff(self):
        now = pygame.time.get_ticks()
        if self.stats.level >= 2 and now - self.last_debuff_time > 5000 and self.aliens:
            kind = random.choice(['slow', 'no_fire', 'lock'])
            alien = random.choice(self.aliens.sprites())
            debuff = EnemyDebuff(self.screen, kind, alien.rect.centerx, alien.rect.bottom)
            self.debuffs.add(debuff)
            self.last_debuff_time = now

    def _check_powerup_collisions(self):
        collisions = pygame.sprite.spritecollide(self.ship, self.powerups, True)
        for p in collisions:
            self._activate_powerup(p.kind)
            self.powerup.play()

    def _activate_powerup(self, kind):
        now = pygame.time.get_ticks()
        if kind == 'shield':
            self.ship.invincible = True
            self.ship.shield_timer = now
        elif kind == 'machine':
            self.ship.machine_gun = True
            self.ship.gun_timer = now
        elif kind == 'double':
            self.ship.double_shot = True
            self.ship.double_timer = now
        elif kind == 'bomb':
            self.bomb.play()
            self._explode_aliens()
        elif kind == 'nuke':
            self.nuke.play()
            self.aliens.empty()
             
    def _check_debuff_collisions(self):
        hits = pygame.sprite.spritecollide(self.ship, self.debuffs, True)
        now = pygame.time.get_ticks()
        self.debuff.play()
        for debuff in hits:
            if debuff.kind == 'slow':
                self.ship.speed_factor = self.settings.ship_speed * 0.5
                self.ship.slow_timer = now
            elif debuff.kind == 'no_fire':
                self.ship.fire_locked = True
                self.ship.fire_timer = now
            elif debuff.kind == 'lock':
                self.ship.locked = True
                self.ship.lock_timer = now

    def _check_powerup_timers(self):
        now = pygame.time.get_ticks()
        if self.ship.invincible and now - self.ship.shield_timer > 5000:
            self.ship.invincible = False
        if self.ship.machine_gun and now - self.ship.gun_timer > 5000:
            self.ship.machine_gun = False
        if self.ship.double_shot and now - self.ship.double_timer > 5000:
            self.ship.double_shot = False    

    def _check_debuff_timers(self):
        now = pygame.time.get_ticks()
        if self.ship.fire_locked and now - self.ship.fire_timer > 5000:
            self.ship.fire_locked = False
        if self.ship.locked and now - self.ship.lock_timer > 3000:
            self.ship.locked = False
        if self.ship.speed_factor < self.settings.ship_speed and now - self.ship.slow_timer > 5000:
            self.ship.speed_factor = self.settings.ship_speed

    def _explode_aliens(self):
        for alien in list(self.aliens)[:4]:
            self.aliens.remove(alien)

    def _ship_hit(self):
        if not self.ship.invincible:
            if self.stats.ships_left > 0:
                self.stats.ships_left -= 1
                self.sb.prep_ships()
                self.aliens.empty()
                self.bullets.empty()
                self.powerups.empty()
                self.debuffs.empty()
                self._create_fleet()
                self.ship.center_ship()
                pygame.time.delay(500)
            else:
                self.game_active = False
                pygame.mouse.set_visible(True)

    def _update_screen(self):
        self.screen.blit(self.bg_image, (0, 0))

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.ship.blitme()
        self.aliens.draw(self.screen)

        for powerup in self.powerups.sprites():
            powerup.draw()
        for debuff in self.debuffs.sprites():
            debuff.draw()
        self.sb.show_score()

        if not self.game_active:
            self.play_button.draw_button()

        for bullet in self.alien_bullets.sprites():
            bullet.draw()

        if self.boss:
            self.boss.draw()
            
        for bullet in self.boss_bullets.sprites():
            bullet.draw()    

        if self.laser_beam_active:
            ship_center_x = self.ship.rect.centerx
            pygame.draw.rect(self.screen, (255, 0, 0), (ship_center_x - 2, 0, 4, self.ship.rect.top))

        pygame.display.flip()  # ✅ Always flip

    def _maybe_alien_fire(self):
        if self.stats.level >= 2:
            fire_chance = 0.002 + (self.stats.level * 0.0015)  # scaling chance
            for alien in self.aliens:
                if random.random() < fire_chance:
                    bullet = AlienBullet(self, alien.rect.centerx, alien.rect.bottom)
                    self.alien_bullets.add(bullet)
                    self.alien_laser.play()
                    
    def _boss_maybe_attack(self):
        now = pygame.time.get_ticks()
        interval = 1800  # ms between attacks

        if now - self.last_boss_attack > interval:
            pattern = random.choice(['laser_burst', 'bomb_drop'])
            
            if pattern == 'laser_burst':
                for offset in [-80, 0, 80]:  # 3 beams
                    x = self.boss.rect.centerx + offset
                    y = self.boss.rect.bottom
                    bullet = BossBullet(self, x, y, kind='laser')
                    self.boss_bullets.add(bullet)
                    self.boss_laser.play()

            elif pattern == 'bomb_drop':
                # 1 large bomb, easier to dodge
                bullet = BossBullet(self, self.boss.rect.centerx, self.boss.rect.bottom, kind='bomb')
                self.boss_bullets.add(bullet)
                self.boss_bomb.play()

            self.last_boss_attack = now
            
    def _check_laser_hits(self):
        ship_center_x = self.ship.rect.centerx
        beam_rect = pygame.Rect(ship_center_x - 2, 0, 4, self.ship.rect.top)

        for alien in self.aliens.copy():
            if beam_rect.colliderect(alien.rect):
                self.aliens.remove(alien)
                self.stats.score += self.settings.alien_points
                self.sb.prep_score()
                self.sb.check_high_score()

        # Optional: Damage the boss
        if self.boss and beam_rect.colliderect(self.boss.rect):
            self.boss.take_damage(1)

        self.player_laser.play()
            
if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
