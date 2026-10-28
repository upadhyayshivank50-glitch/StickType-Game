import pygame
import sys
import random
import math

# Pygame initialize
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stickman Gear Shift (MHA Style) - Pygame Animation")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
NEON_BLUE = (0, 220, 255)
DARK_BLUE = (0, 100, 180)
SHOCKWAVE_COLOR = (100, 240, 255)

# Shockwave Ring Class for Sonic-Boom Effect
class Shockwave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 120
        self.alpha = 255

    def update(self):
        self.radius += 6
        self.alpha = max(0, 255 - int((self.radius / self.max_radius) * 255))

    def draw(self, surface):
        if self.radius < self.max_radius:
            # Drawing concentric shockwave rings
            surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*SHOCKWAVE_COLOR, self.alpha), (int(self.x), int(self.y)), int(self.radius), 3)
            pygame.draw.circle(surf, (*NEON_BLUE, max(0, self.alpha - 100)), (int(self.x), int(self.y)), int(self.radius * 0.7), 2)
            surface.blit(surf, (0, 0))

# Character Class with Gear Shift State Machine
class StickmanGearShift:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = BLACK
        self.dir = 1  # 1 for right, -1 for left
        self.state = "IDLE"
        self.anim_timer = 0
        self.dodge_offset = 0
        self.gear_angle = 0
        self.screen_shake = 0

    def trigger_gear_shift(self):
        if self.state == "IDLE":
            self.state = "GEAR_WINDUP"
            self.anim_timer = 0

    def update(self):
        self.gear_angle += 8  # Rotate mechanical cogs continuously during animation

        if self.state == "GEAR_WINDUP":
            self.anim_timer += 1
            # Slight anticipation/crouch
            if self.anim_timer == 1:
                shockwaves.append(Shockwave(self.x, self.y - 80))
            if self.anim_timer > 20:
                self.state = "GEAR_DODGE"
                self.anim_timer = 0
                self.screen_shake = 12

        elif self.state == "GEAR_DODGE":
            self.anim_timer += 1
            # Fast high-speed dodge backward with acceleration
            self.dodge_offset = -min(self.anim_timer * 12, 160)
            
            if self.anim_timer > 25:
                self.state = "IDLE"
                self.dodge_offset = 0

    def draw(self, surface, shake_x, shake_y):
        curr_x = self.x + self.dodge_offset + shake_x
        curr_y = self.y + shake_y

        # --- DRAW NEON-BLUE ANIME MECHANICAL COGS (GEARS) ---
        if self.state != "IDLE":
            cog_center = (int(curr_x), int(curr_y - 80))
            # Draw rotating mechanical gear teeth / circles
            for r_mult, count in [(1.2, 8), (1.6, 12)]:
                r = int(45 * r_mult)
                for i in range(count):
                    angle = math.radians(self.gear_angle * (1 if r_mult > 1.3 else -1) + (i * (360 / count)))
                    hx = cog_center[0] + int(r * math.math.cos(angle) if hasattr(math, 'math') else r * math.cos(angle))
                    hy = cog_center[1] + int(r * math.sin(angle))
                    pygame.draw.circle(surface, NEON_BLUE, (hx, hy), 5)
                pygame.draw.circle(surface, NEON_BLUE, cog_center, r, 2)

        # # Head & Body Structure
        pygame.draw.circle(surface, self.color, (int(curr_x), int(curr_y - 140)), 30, 0)
        pygame.draw.line(surface, self.color, (int(curr_x), int(curr_y - 110)), (int(curr_x), int(curr_y - 50)), 10)

        # # Arms Drawing based on state
        shoulder_y = int(curr_y - 106)
        
        if self.state == "IDLE":
            # Normal relaxed arms
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x - (30 * self.dir)), int(curr_y - 112)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x - (24 * self.dir)), int(curr_y - 112)), (int(curr_x - (36 * self.dir)), int(curr_y - 76)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x - (36 * self.dir)), int(curr_y - 76)), (int(curr_x - (54 * self.dir)), int(curr_y - 76)), 10)
            
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x + (30 * self.dir)), int(curr_y - 112)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x + (24 * self.dir)), int(curr_y - 112)), (int(curr_x + (46 * self.dir)), int(curr_y - 80)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x + (46 * self.dir)), int(curr_y - 80)), (int(curr_x + (10 * self.dir)), int(curr_y - 80)), 10)

        else:
            # Gear Shift Active Pose (Defensive / High-speed motion arms)
            pygame.draw.line(surface, DARK_BLUE, (int(curr_x), shoulder_y), (int(curr_x - (40 * self.dir)), int(curr_y - 120)), 12)
            pygame.draw.line(surface, DARK_BLUE, (int(curr_x), shoulder_y), (int(curr_x + (35 * self.dir)), int(curr_y - 90)), 12)

        # # Legs and Thighs Structure
        l_hip = (int(curr_x), int(curr_y - 50))
        l_knee = (int(curr_x - (28 * self.dir)), int(curr_y - 28))
        l_ankle = (int(curr_x - (44 * self.dir)), int(curr_y - 14))
        l_foot = (int(curr_x - (48 * self.dir)), int(curr_y))

        pygame.draw.line(surface, self.color, l_hip, l_knee, 10)
        pygame.draw.line(surface, self.color, l_knee, l_ankle, 10)
        pygame.draw.line(surface, self.color, l_ankle, l_foot, 10)

        r_hip = (int(curr_x), int(curr_y - 50))
        r_knee = (int(curr_x + (28 * self.dir)), int(curr_y - 30))
        r_ankle = (int(curr_x + (38 * self.dir)), int(curr_y - 15))
        r_foot = (int(curr_x + (44 * self.dir)), int(curr_y))

        pygame.draw.line(surface, self.color, r_hip, r_knee, 10)
        pygame.draw.line(surface, self.color, r_knee, r_ankle, 10)
        pygame.draw.line(surface, self.color, r_ankle, r_foot, 10)

# Setup Game Loop
player = StickmanGearShift(450, 450)
shockwaves = []

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.trigger_gear_shift()

    # Update player state
    player.update()

    # Update shockwaves
    for sw in shockwaves[:]:
        sw.update()
        sw.draw(screen)
        if sw.alpha <= 0:
            shockwaves.remove(sw)

    # Calculate Screen Shake
    shake_x = random.randint(-player.screen_shake, player.screen_shake) if player.screen_shake > 0 else 0
    shake_y = random.randint(-player.screen_shake, player.screen_shake) if player.screen_shake > 0 else 0
    if player.screen_shake > 0:
        player.screen_shake -= 1

    # Draw Player
    player.draw(screen, shake_x, shake_y)

    # UI Instructions text
    font = pygame.font.SysFont(None, 24)
    txt = font.render("Press [SPACE] to trigger GEAR SHIFT (MHA Anime Style)", True, BLACK)
    screen.blit(txt, (20, 20))

    pygame.display.flip()
    clock.tick(60)