import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load images (replace with your sprite paths)
player_img = pygame.image.load(os.path.join("assets", "player_ship.png")).convert_alpha()
enemy_img = pygame.image.load(os.path.join("assets", "enemy_ship.png")).convert_alpha()
player_laser_img = pygame.image.load(os.path.join("assets", "player_laser_blue.png")).convert_alpha()
enemy_laser_img = pygame.image.load(os.path.join("assets", "enemy_laser_red_2.png")).convert_alpha()
background_img = pygame.image.load(os.path.join("assets", "space_background.png")).convert()

# Scale images for crisp visuals
player_img = pygame.transform.scale(player_img, (60, 60))
enemy_img = pygame.transform.scale(enemy_img, (50, 50))
player_laser_img = pygame.transform.scale(player_laser_img, (30, 40))
enemy_laser_img = pygame.transform.scale(enemy_laser_img, (30, 40))
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        # Support both arrow keys and WASD controls for left/right movement
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 0:
            self.rect.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

# Laser class
class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_enemy=False):
        super().__init__()
        self.image = enemy_laser_img if is_enemy else player_laser_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = -10 if not is_enemy else 10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.direction = 1
        self.laser_timer = random.randint(50, 150)

    def update(self):
        self.rect.x += self.speed * self.direction
        self.laser_timer -= 1
        if self.laser_timer <= 0:
            laser = Laser(self.rect.centerx, self.rect.bottom, 1, is_enemy=True)
            all_sprites.add(laser)
            enemy_lasers.add(laser)
            self.laser_timer = random.randint(50, 150)

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_lasers = pygame.sprite.Group()
enemy_lasers = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Enemy spawning configuration
enemy_start_x = 100  # Start position from left edge
enemy_start_y = 80   # Start position from top
enemy_spacing_x = 70  # Horizontal spacing between enemies
enemy_spacing_y = 60  # Vertical spacing between rows
enemy_rows = 4        # Number of enemy rows
enemies_per_row = 9  # Number of enemies per row
total_enemies = enemy_rows * enemies_per_row

# Enemy spawning variables
enemies_spawned = 0
spawn_timer = 0
spawn_delay = 50  # Frames between enemy spawns (adjust for speed)
current_row = 0
current_col = 0

# Game variables
score = 0
font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()
running = True

# Main game loop
while running:
    clock.tick(60)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                laser = Laser(player.rect.centerx, player.rect.top, -1)
                all_sprites.add(laser)
                player_lasers.add(laser)

    # Update
    all_sprites.update()

    # Progressive enemy spawning
    if enemies_spawned < total_enemies:
        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            # Spawn next enemy in formation
            x = enemy_start_x + (current_col * enemy_spacing_x)
            y = enemy_start_y + (current_row * enemy_spacing_y)
            enemy = Enemy(x, y)
            all_sprites.add(enemy)
            enemies.add(enemy)
            
            enemies_spawned += 1
            current_col += 1
            
            # Move to next row when current row is full
            if current_col >= enemies_per_row:
                current_col = 0
                current_row += 1
            
            spawn_timer = 0

    # Enemy movement (wave-like)
    for enemy in enemies:
        if enemy.rect.right > SCREEN_WIDTH or enemy.rect.left < 0:
            for e in enemies:
                e.rect.y += 20
                e.direction *= -1

    # Collisions
    if pygame.sprite.spritecollide(player, enemies, False) or pygame.sprite.spritecollide(player, enemy_lasers, False):
        running = False

    hits = pygame.sprite.groupcollide(enemies, player_lasers, True, True)
    for hit in hits:
        score += 10
        if random.random() < 0.15:  # 15% chance to spawn new enemy
            # Spawn new enemy in a more controlled way
            spawn_x = random.randint(100, SCREEN_WIDTH - 100)
            spawn_y = 50
            
            # Check if spawn position is too close to existing enemies
            spawn_rect = pygame.Rect(spawn_x - 40, spawn_y - 40, 80, 80)
            too_close = False
            for existing_enemy in enemies:
                if spawn_rect.colliderect(existing_enemy.rect):
                    too_close = True
                    break
            
            if not too_close:
                enemy = Enemy(spawn_x, spawn_y)
                all_sprites.add(enemy)
                enemies.add(enemy)

    # Draw
    screen.blit(background_img, (0, 0))
    all_sprites.draw(screen)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()

# Game over
game_over_text = font.render(f"Game Over! Score: {score}", True, RED)
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
pygame.display.flip()
pygame.time.wait(2000)

pygame.quit()