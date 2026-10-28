import sys
import pygame
import random
import json
import os
import string
import math

import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

SCORE_FILE = "scores.json"

# Scores-------------------------------------------------------------------
def load_scores():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

# Time format-----------------------------------------------------------------------
def format_time(total_seconds):
    minutes = int(total_seconds) // 60
    seconds = int(total_seconds) % 60
    return f"{minutes:02}:{seconds:02}"

def time_to_seconds(time_str):
    try:
        parts = time_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 0

# Storage
def save_score(name, final_score, accuracy_val= 0.0, time_taken=0):
    scores = load_scores()
    scores.append({
        "name": str(name),
        "score": int(final_score),
        "accuracy": f"{accuracy_val: .1f}%",
        "time": format_time(time_taken),
    })
    scores = sorted(scores, key=lambda x: (x["score"], -time_to_seconds(x.get("time", "00:00"))), reverse=True)
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)

def clear_scores():
    if os.path.exists(SCORE_FILE):
        os.remove(SCORE_FILE)

# UI--------------------------------------------------------------------------------
def draw_arcade_button(surface, rect, text, font, base_color, text_color=(255, 255, 255), is_hovered=False):
    draw_rect = rect.copy()
    if is_hovered:
        draw_rect.inflate_ip(12, 8)

    shadow_rect = draw_rect.copy()
    shadow_rect.y += 8

    pygame.draw.rect(surface, (10, 10, 10), shadow_rect, border_radius=20)
    pygame.draw.rect(surface, base_color, draw_rect, border_radius=20)
    pygame.draw.rect(surface, (155, 255, 255), draw_rect, 4, border_radius=20)

    text_surf = font.render(text, True, text_color)
    surface.blit(text_surf, text_surf.get_rect(center=draw_rect.center))

# Player Kunai / Fireball Projectile Class
class Projectile:
    def __init__(self, x, y, facing_right, target_x, is_fireball=False, on_hit_callback=None):
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.speed = 45 if facing_right else -45
        self.target_x = target_x
        self.active = True
        self.is_fireball = is_fireball
        self.on_hit_callback = on_hit_callback

    def update(self):
        self.x += self.speed
        if self.facing_right and self.x >= self.target_x:
            self.active = False
            if self.on_hit_callback:
                self.on_hit_callback()
        elif not self.facing_right and self.x <= self.target_x:
            self.active = False
            if self.on_hit_callback:
                self.on_hit_callback()

    def draw(self, surface):
        dir = 1 if self.facing_right else -1
        if self.is_fireball:
            center = (int(self.x), int(self.y))
            pygame.draw.circle(surface, (255, 69, 0), center, 24)
            pygame.draw.circle(surface, (255, 140, 0), center, 16)
            pygame.draw.circle(surface, (255, 255, 0), center, 8)
        else:
            tip_x = self.x + (25 * dir)
            base_x = self.x - (10 * dir)
            
            # White glow outline for player's kunai
            pygame.draw.line(surface, (255, 255, 255), (base_x - (2 * dir), self.y), (tip_x + (2 * dir), self.y), 12)
            pygame.draw.line(surface, (200, 220, 255), (base_x, self.y - 4), (tip_x, self.y - 4), 6)
            
            pygame.draw.line(surface, (20, 20, 20), (base_x, self.y), (tip_x, self.y), 6)
            pygame.draw.line(surface, (120, 120, 120), (base_x, self.y - 2), (tip_x, self.y - 2), 2)
            ring_x = self.x - (16 * dir)
            pygame.draw.circle(surface, (255, 255, 255), (int(ring_x), int(self.y)), 8, 3)
            pygame.draw.circle(surface, (20, 20, 20), (int(ring_x), int(self.y)), 6, 3)

# Enemy Projectile Class
class EnemyProjectile:
    def __init__(self, x, y, facing_right, target_x, damage, on_hit_callback=None):
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.damage = damage
        self.speed = -45 if not facing_right else 45
        self.target_x = target_x
        self.active = True
        self.rotation = 0
        self.on_hit_callback = on_hit_callback

    def update(self):
        self.x += self.speed
        self.rotation += 25
        if not self.facing_right and self.x <= self.target_x:
            self.active = False
            if self.on_hit_callback:
                self.on_hit_callback()
        elif self.facing_right and self.x >= self.target_x:
            self.active = False
            if self.on_hit_callback:
                self.on_hit_callback()

    def draw(self, surface):
        if self.damage <= 5:
            # SHURIKEN (Damage 1 to 5)
            size = 14
            center = (int(self.x), int(self.y))
            points = []
            for i in range(4):
                angle = math.radians(self.rotation + i * 90)
                outer_x = center[0] + math.cos(angle) * size
                outer_y = center[1] + math.sin(angle) * size
                points.append((outer_x, outer_y))
                inner_angle = math.radians(self.rotation + 45 + i * 90)
                inner_x = center[0] + math.cos(inner_angle) * (size / 3)
                inner_y = center[1] + math.sin(inner_angle) * (size / 3)
                points.append((inner_x, inner_y))
            pygame.draw.polygon(surface, (40, 40, 40), points)
            pygame.draw.circle(surface, (200, 200, 200), center, 3)
        else:
            # FIREBALL (Damage 6 to 10)
            center = (int(self.x), int(self.y))
            pygame.draw.circle(surface, (255, 69, 0), center, 24)
            pygame.draw.circle(surface, (255, 140, 0), center, 16)
            pygame.draw.circle(surface, (255, 255, 0), center, 8)

# Sparks (Kunai hit)
class Spark:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-12, -3)
        self.life = int(18)
        self.color = random.choice([(255, 255, 255), (255, 200, 0), (255, 50, 50)])
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.8
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Fire Particles (Fireball hit)
class FireParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-12, 12)
        self.vy = random.uniform(-14, -2)
        self.life = int(25)
        self.color = random.choice([(255, 69, 0), (255, 140, 0), (255, 255, 0), (200, 50, 0)])
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.4
        self.size = max(1, self.size - 0.2)
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Stickman Class
class Stickman:
    def __init__(self, x, y, color, facing_right=True):
        self.x = x
        self.y = y
        self.color = color
        self.facing_right = facing_right
        self.hp = 300
        self.display_hp = 300.0
        self.ghost_hp = 300.0
        self.max_hp = 300
        self.breath_time = random.uniform(0, 100)
        self.breath_offset = 0

        self.state = "IDLE"  
        self.anim_timer = 0
        self.projectiles = [] # List to support multiple projectiles per keypress
        self.enemy_projectile = None
        self.hit_sparks = []
        self.recoil_offset = 0  
        self.target_enemy = None
        self.attack_damage = 1

    def trigger_recoil(self):
        self.state = "HIT"
        self.recoil_offset = 18 if not self.facing_right else -18

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def start_throw(self, target_enemy, is_fireball=False):
        if self.hp > 0:
            self.state = "WINDUP"
            self.anim_timer = 0
            self.target_enemy = target_enemy
            self.pending_fireball = is_fireball

    def start_enemy_attack(self, target_enemy, damage):
        if self.hp > 0:
            self.state = "WINDUP"
            self.anim_timer = 0
            self.target_enemy = target_enemy
            self.attack_damage = damage
        if damage <= 5:
            kunai_sound.play()
            kunai_sound.set_volume(0.2)
        else:
            fireball_sound.play()
            fireball_sound.set_volume(0.2)

    def update(self, target_x):
        if self.display_hp > self.hp:
            self.display_hp = max(float(self.hp), self.display_hp - 4.0)
        elif self.display_hp < self.hp:
            self.display_hp = min(float(self.hp), self.display_hp + 4.0)

        if self.ghost_hp > self.hp:
            self.ghost_hp = max(float(self.hp), self.ghost_hp - 2.5)

        self.breath_time += 0.04
        self.breath_offset = math.sin(self.breath_time) * 3.6

        if self.recoil_offset != 0:
            self.recoil_offset *= 0.75
            if abs(self.recoil_offset) < 0.5:
                self.recoil_offset = 0
                if self.state == "HIT":
                    self.state = "IDLE"

        if self.state == "WINDUP":
            self.anim_timer += 1
            if self.anim_timer > 4:
                self.state = "THROW"
                self.anim_timer = 0
                
                if self.facing_right:
                    start_x = self.x + 30
                    is_fb = getattr(self, 'pending_fireball', False)
                    def make_callback(fb):
                        def on_projectile_hit():
                            if self.target_enemy:
                                hit_dmg = 3 if fb else 1
                                self.target_enemy.take_damage(hit_dmg)
                                self.target_enemy.trigger_recoil()
                                if fb:
                                    for _ in range(12):
                                        self.hit_sparks.append(FireParticle(self.target_enemy.x, self.target_enemy.y - 70))
                                else:
                                    for _ in range(6):
                                        self.hit_sparks.append(Spark(self.target_enemy.x, self.target_enemy.y - 70))
                        return on_projectile_hit

                    new_proj = Projectile(start_x, self.y - 100, self.facing_right, target_x, is_fireball=is_fb, on_hit_callback=make_callback(is_fb))
                    self.projectiles.append(new_proj)
                else:
                    start_x = self.x - 30
                    def on_enemy_hit():
                        if self.target_enemy:
                            self.target_enemy.take_damage(self.attack_damage)
                            self.target_enemy.trigger_recoil()
                            if self.attack_damage > 5:
                                for _ in range(12):
                                    self.hit_sparks.append(FireParticle(self.target_enemy.x, self.target_enemy.y - 70))
                            else:
                                for _ in range(6):
                                    self.hit_sparks.append(Spark(self.target_enemy.x, self.target_enemy.y - 70))
                    self.enemy_projectile = EnemyProjectile(start_x, self.y - 100, self.facing_right, target_x, self.attack_damage, on_hit_callback=on_enemy_hit)

        elif self.state == "THROW":
            self.anim_timer += 1
            if self.anim_timer > 5:
                self.state = "IDLE"
                self.anim_timer = 0

        for proj in self.projectiles[:]:
            proj.update()
            if not proj.active:
                self.projectiles.remove(proj)

        if self.enemy_projectile:
            self.enemy_projectile.update()
            if not self.enemy_projectile.active:
                self.enemy_projectile = None

        for spark in self.hit_sparks[:]:
            spark.update()
            if spark.life <= 0:
                self.hit_sparks.remove(spark)

    def draw(self, surface):
        dir = 1 if self.facing_right else -1
        if self.hp <= 0 and self.display_hp <= 0:
            return
        
        curr_x = self.x + self.recoil_offset
        curr_y = self.y + self.breath_offset

        # Visual Depth: Shadow/Depth Ellipse on Ground
        shadow_rect = pygame.Rect(int(curr_x - 24), int(self.y - 6), 48, 14)
        pygame.draw.ellipse(surface, (10, 10, 15), shadow_rect)

        # Head & Body
        pygame.draw.circle(surface, self.color, (int(curr_x), int(curr_y - 140)), 30, 0)
        pygame.draw.line(surface, self.color, (int(curr_x), int(curr_y - 110)), (int(curr_x), int(curr_y - 50)), 10)
        
        # Arms Drawing based on state
        shoulder_y = int(curr_y - 106)
        if self.state == "IDLE" or self.state == "HIT":
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x - (30 * dir)), int(curr_y - 112)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x - (24 * dir)), int(curr_y - 112)), (int(curr_x - (36 * dir)), int(curr_y - 76)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x - (36 * dir)), int(curr_y - 76)), (int(curr_x - (54 * dir)), int(curr_y - 60)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x + (30 * dir)), int(curr_y - 112)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x + (24 * dir)), int(curr_y - 112)), (int(curr_x + (46 * dir)), int(curr_y - 80)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x + (46 * dir)), int(curr_y - 80)), (int(curr_x + (10 * dir)), int(curr_y - 96)), 10)
        elif self.state == "WINDUP":
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x - (55 * dir)), int(curr_y - 130)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x + (20 * dir)), int(curr_y - 100)), 10)
        elif self.state == "THROW":
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x + (65 * dir)), int(curr_y - 115)), 10)
            pygame.draw.line(surface, self.color, (int(curr_x), shoulder_y), (int(curr_x - (25 * dir)), int(curr_y - 105)), 10)

        # Legs and Thighs Structure
        l_hip = (int(curr_x), int(curr_y - 50))
        l_knee = (int(curr_x - (28 * dir)), int(curr_y - 28))
        l_ankle = (int(curr_x - (44 * dir)), int(curr_y - 14))
        l_foot = (int(curr_x - (48 * dir)), int(self.y))
        
        pygame.draw.line(surface, self.color, l_hip, l_knee, 10)
        pygame.draw.line(surface, self.color, l_knee, l_ankle, 10)
        pygame.draw.line(surface, self.color, l_ankle, l_foot, 10)

        r_hip = (int(curr_x), int(curr_y - 50))
        r_knee = (int(curr_x + (28 * dir)), int(curr_y - 30))
        r_ankle = (int(curr_x + (38 * dir)), int(curr_y - 15))
        r_foot = (int(curr_x + (44 * dir)), int(self.y))
        
        pygame.draw.line(surface, self.color, r_hip, r_knee, 10)
        pygame.draw.line(surface, self.color, r_knee, r_ankle, 10)
        pygame.draw.line(surface, self.color, r_ankle, r_foot, 10)

        for proj in self.projectiles:
            proj.draw(surface)
        if self.enemy_projectile:
            self.enemy_projectile.draw(surface)
        for spark in self.hit_sparks:
            spark.draw(surface)

# Setup Screen Dimensions FIRST (HD 1600x1000)
Width = 1600
Height = 1000
screen = pygame.display.set_mode((Width // 2, Height // 2), pygame.RESIZABLE)
virtual_screen = pygame.Surface((Width, Height))
pygame.display.set_caption("StickType")
clock = pygame.time.Clock()
pause_btn_rect = pygame.Rect(Width - 100, 30, 70, 60) 

# Variables----------------------------------------------------------------------------
current_ticks = 0
p1_name = ""
p2_name = "MADARA"
score = 0
start_time = 0
game_over = False
score_saved = False  
dt = 0.0
frozen_time = 0
current_time = 0  
timer_started = False
play_btn_rect = None
exit_btn_rect = None
last_word = None
special_word_active = False
current_special_word = ""
normal_word_typed_counter = 0
input_active = False
streak = 0
max_streak_for_bar = 10
streak_bar_fill = 0.0
word_completed = False
special_attack_active = False
wrong_key_pressed = False
final_result_text = ""
in_menu = True

banner_scale = 0.0
susanoo_scale = 0.0
scroll_offset = 0
target_scroll_offset = 0

madara_susanoo_active = False
susanoo_timer_started = False
susanoo_start_time = 0
susanoo_duration = 6000
susanoo_triger_timer = 0
susanoo_cooldown = 25000

susanoo_target_sequence = ""
susanoo_seq_index = 0
susanoo_defended = False
madara_post_invincibility = False
post_invincibility_start_time = 0

last_input_time = 0
afk_warning_active = False
in_scoreboard = False
back_btn_rect = None
reset_btn_rect = None
scores = load_scores()
key_squeeze_scale = 1.0
boost_active = False
boost_timer = 0
boost_duration = 15000
max_game_streak = 0
paused = False

shake_timer= 0
slash_anim_timer = 0

# SSJ Charge-up Animation Variables
ssj_charging = False
ssj_charge_timer = 0
ssj_charge_duration = 90  # frames (~1.5 seconds)

game_over_alpha = 0
wrong_key_flash_timer = 0

total_keystrokes = 0
correct_keystrokes = 0
accuracy = 100.0
madara_played = False

# Sharingan Frames Load karna
sharingan_frames = []
for i in range(27): # 00 se 26 tak tere frames
    frame_name = f"frame_{i:02d}_delay-0.1s.gif" 
    try:
        # Load karke seedha full screen size (Width, Height) ka kar diya
        img = pygame.image.load(frame_name).convert()
        img = pygame.transform.scale(img, (Width, Height))
        # Transparency set karna (0 ekdum gayab, 255 ekdum solid. 120 mast semi-transparent lagega)
        img.set_alpha(120) 
        sharingan_frames.append(img)
    except:
        pass

# Instructions popup variables & images
show_instructions = False
img_box = pygame.Rect(0, 0, 0, 0)
instructions_page = 0
total_instructions_pages = 5
close_help_rect = pygame.Rect(0, 0, 0, 0)
next_btn_rect = pygame.Rect(0, 0, 0, 0)
prev_btn_rect = pygame.Rect(0, 0, 0, 0)
popup_rect = pygame.Rect(280, 40, Width - 560, Height - 80)
instructions_images = [
    pygame.image.load("1.png"),
    pygame.image.load("2.png"),
    pygame.image.load("3.png"),
    pygame.image.load("4.png"),
    pygame.image.load("5.png")
]
# VOICE-------------------------------------------------

logo_img = pygame.image.load("StickType.png").convert_alpha()
logo_img = pygame.transform.scale(logo_img, (920, 280))

click_sound = pygame.mixer.Sound("mouse_click.mp3")
click_sound.set_volume(0.3)

kunai_sound = pygame.mixer.Sound("kunai.mp3")
kunai_sound.set_volume(0.5)

fireball_sound = pygame.mixer.Sound("fire-ball.mp3")
fireball_sound.set_volume(0.5)

key_sound = pygame.mixer.Sound("keyboard-single-click.mp3")
key_sound.set_volume(0.5)

pageflip_sound = pygame.mixer.Sound("pageflip.mp3")
pageflip_sound.set_volume(0.5)


delete_sound = pygame.mixer.Sound("delete_button.mp3")
delete_sound.set_volume(0.1)

ssj_sound = pygame.mixer.Sound("ssj.mp3")
ssj_sound.set_volume(0.1)

madara_dialog= pygame.mixer.Sound("madara.wav")
madara_dialog.set_volume(0.5)

red_hawk= pygame.mixer.Sound("redhawk.mp3")
red_hawk.set_volume(0.5)

rasenshuriken= pygame.mixer.Sound("rasenshuriken.mp3")
rasenshuriken.set_volume(0.5)

chidori= pygame.mixer.Sound("chidorii.mp3")
chidori.set_volume(0.5)

blackflash= pygame.mixer.Sound("black-flash.mp3")
blackflash.set_volume(0.5)

dimensionslash= pygame.mixer.Sound("dimensionslash.mp3")
dimensionslash.set_volume(0.5)

amaterasu= pygame.mixer.Sound("amaterasu.mp3")
amaterasu.set_volume(0.5)

kamehameha= pygame.mixer.Sound("kamehameha.mp3")
kamehameha.set_volume(0.5)

zankanotachi= pygame.mixer.Sound("zanka-no-tachi.mp3")
zankanotachi.set_volume(0.5)

gearshift= pygame.mixer.Sound("gearshift.mp3")
gearshift.set_volume(0.5)

fuga= pygame.mixer.Sound("fuga.mp3")
fuga.set_volume(0.5)

pathetic= pygame.mixer.Sound("pathetic.mp3")
pathetic.set_volume(0.5)


#--------------------------------------------------------------
running = True
bg_img = pygame.image.load("background.png")
bg_img = pygame.transform.scale(bg_img, (Width, Height))

waiting_for_space = False

banner_text = "Enjoy"
banner_timer = 90

TASKBAR_HEIGHT = 0
taskbar_rect = pygame.Rect(0, Height - TASKBAR_HEIGHT, Width, TASKBAR_HEIGHT)
TASKBAR_BLACK = (139, 90, 43)
ground_y = Height - 80

player1 = Stickman(400, ground_y, (255, 255, 255), facing_right=True)
player2 = Stickman(1200, ground_y, (0, 0, 0), facing_right=False)

font_game = pygame.font.Font("Lato-Bold.ttf", 90)
main_font = pygame.font.SysFont("Arial", 35, bold=True)
font_banner = pygame.font.Font("Lato-Bold.ttf", 90)
font_ui = pygame.font.SysFont("Arial Black", 35, bold=True)
word_font = pygame.font.SysFont("impact", 30)
font_f = pygame.font.SysFont("trebuchet ms", 80, bold=True)
vs_font = pygame.font.SysFont(None, 110, bold=True)
name_font = pygame.font.SysFont(None, 30, )
font_f2 = pygame.font.SysFont("trebuchet ms", 60, bold=True)

enemy_attack_timer = 0
enemy_attack_cooldown = 4000

SPECIAL_WORD_POOL = [
    "RED HAWK", "RASENSHURIKEN", "CHIDORI", "BLACK FLASH", "DIMENSION SLASH",
    "AMATERASU", "KAMEHAMEHA", "ZANKA NO TACHI", "GEAR SHIFT", "FUGA"
]

WORD_POOL = {
    "EASY": [
        "THE", "AND", "MAKE", "JUST", "WORK", "TIME", "GOOD", "KNOW", "TAKE", "PEOPLE",
        "INTO", "YEAR", "YOUR", "SOME", "THEM", "THAN", "LOOK", "ONLY", "COME", "OVER",
        "THEN", "NOW", "ALSO", "BACK", "LIFE", "FIND", "GIVE", "TELL", "WORK", "CALL", 
        "TRY", "ASK", "NEED", "FEEL", "LEAVE", "PUT", "KEEP", "BEGIN", "SEEM", "HELP", 
        "TALK", "TURN", "START", "SHOW", "HEAR"
    ],
    "MEDIUM": [
        "ACTION", "SYSTEM", "PLAYER", "RECORD", "FUTURE", "CHANGE", "BETTER", "NUMBER",
        "ALWAYS", "MOTHER", "FATHER", "FRIEND", "GROUND", "EFFECT", "RESULT", "METHOD",
        "OFFICE", "DESIGN", "BECOME", "LITTLE", "PUBLIC", "SCHOOL", "REPORT", "PERIOD",
        "MOMENT", "VECTOR", "SHADOW", "BLADE", "STRIKE", "FORCE", "COMBAT", "DEFEND", 
        "ATTACK", "TARGET", "ENERGY", "MISSION", "VECTOR", "ONLINE", "STATUS", "GLOBAL", 
        "MARKET", "PLANET", "STREAM", "PORTAL", "DEVICE"
    ],
    "HARD": [
        "PRACTICE", "ACCURACY", "STRATEGY", "CHALLENGE", "QUESTION", "BUSINESS",
        "STRENGTH", "MOVEMENT", "TOGETHER", "POSSIBLE", "BUILDING", "COMPUTER",
        "INTEREST", "SECURITY", "KNOWLEDGE", "LEARNING", "RESEARCH", "DEVELOPMENT",
        "EXPERIENCE", "PRODUCTION", "TECHNOLOGY", "MANAGEMENT", "EFFICIENCY",
        "PERFORMANCE", "BACKGROUND", "ILLOGICAL", "SUDDENLY", "CONGRATULATIONS", 
        "ALGORITHM", "DIRECTIONS", "FOUNDATION", "GENERATION", "INNOVATION", "LEADERSHIP", 
        "MANAGEMENT", "NAVIGATION", "OPERATIONS", "POPULATION", "RECOGNITION", "SOLUTION", 
        "TRANSACTION", "UNDERSTAND", "VISIBILITY", "WARRANTY", "YIELDING", "ZEALOUSLY", 
        "ARCHITECT", "BACKGROUND"
    ]
}

def get_random_word(score):
    global last_word
    category = random.choice(["EASY", "MEDIUM", "HARD"])
    word = random.choice(WORD_POOL[category])

    while word == last_word and len(WORD_POOL[category]) > 1:
        word = random.choice(WORD_POOL[category])

    last_word = word
    return word, category

typed_index = 0
current_word, current_category = get_random_word(0)

red_fog_surface = pygame.Surface((Width, Height))
red_fog_surface.fill((180, 0, 0))
red_fog_surface.set_alpha(30)

play_btn_rect = pygame.Rect(0, 0, 0, 0)
score_btn_rect = pygame.Rect(0, 0, 0, 0)
exit_btn_rect = pygame.Rect(0, 0, 0, 0)
back_btn_rect = pygame.Rect(0, 0, 0, 0)
reset_btn_rect = pygame.Rect(0, 0, 0, 0)
help_btn_rect = pygame.Rect(Width - 120, 40, 80, 80)

# Reset------------------------------------------------------------------------------
def reset_game():
    global score, typed_index, waiting_for_space, timer_started, start_time, game_over, score_saved
    global streak, max_game_streak, streak_bar_fill, special_attack_active, boost_active
    global madara_susanoo_active, susanoo_defended, susanoo_seq_index, madara_post_invincibility
    global susanoo_triger_timer, enemy_attack_timer, last_input_time, afk_warning_active, paused, susanoo_cooldown
    global total_keystrokes, correct_keystrokes, accuracy, susanoo_start_time, ssj_charging, ssj_charge_timer
    global shake_timer, slash_anim_timer, last_word, madara_played,key_squeeze_scale

    total_keystrokes = 0
    correct_keystrokes = 0
    accuracy = 100.0

    current_ticks = pygame.time.get_ticks()
    game_over = False
    score_saved = False  
    score = 0
    typed_index = 0
    waiting_for_space = False
    timer_started = False
    start_time = current_ticks
    
    shake_timer = 0
    key_squeeze_scale = 1.0
    slash_anim_timer= 0
    last_word= None
    special_word_active = False
    current_special_word = ""
    normal_word_typed_counter = 0
    current_word, current_category = get_random_word(score)

    player1.hp = player1.max_hp
    player1.display_hp = float(player1.max_hp)
    player1.ghost_hp = float(player1.max_hp)

    player2.hp = player2.max_hp
    player2.display_hp = float(player2.max_hp)
    player2.ghost_hp = float(player2.max_hp)
    
    madara_susanoo_active = False
    susanoo_defended = False
    susanoo_seq_index = 0
    madara_post_invincibility = False
    susanoo_start_time = current_ticks
    susanoo_triger_timer = current_ticks + 20000  
    susanoo_cooldown = random.randint(25000, 30000)
    enemy_attack_timer = current_ticks + 3000 
    
    streak = 0
    max_game_streak = 0
    streak_bar_fill = 0.0
    special_attack_active = False
    boost_active = False
    ssj_charging = False
    ssj_charge_timer = 0
    
    last_input_time = current_ticks
    afk_warning_active = False
    paused = False
    madara_dialog.stop()

    global game_over_alpha
    game_over_alpha = 0
    madara_played= False


# Advanced Healthbar with Ghost Bar & Rolling Counter Numbers
def draw_advanced_health_bar(surface, x, y, stickman, width=360, height=28, is_right_side=False):
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (30, 30, 30), bg_rect, border_radius=10)
    pygame.draw.rect(surface, (255, 255, 255), bg_rect, 4, border_radius=10)
    
    if stickman.max_hp <= 0:
        return

    # 1. Ghost Bar (White trailing bar behind actual HP)
    ghost_fill_width = int((max(0, min(stickman.ghost_hp, stickman.max_hp)) / stickman.max_hp) * width)
    if ghost_fill_width > 0:
        pygame.draw.rect(surface, (220, 220, 220), (x, y, ghost_fill_width, height), border_radius=10)

    # 2. Actual Health Bar
    hp_clamped = max(0, min(stickman.hp, stickman.max_hp))
    fill_width = int((hp_clamped / stickman.max_hp) * width)
    
    if stickman.hp > 200:
        bar_color = (50, 205, 50)
    elif stickman.hp > 100:
        bar_color = (255, 215, 0)
    else:
        bar_color = (220, 20, 60)

    if fill_width > 0:
        pygame.draw.rect(surface, bar_color, (x, y, fill_width, height), border_radius=10)

    # 3. Health Numbers on Top Corner (Rolling Counter format)
    hp_text_str = f"{int(stickman.display_hp)}/{stickman.max_hp}"
    num_surf = word_font.render(hp_text_str, True, (255, 255, 255))
    
    if is_right_side:
        num_rect = num_surf.get_rect(topright=(x + width-300, y - 26))
    else:
        num_rect = num_surf.get_rect(topleft=(x+300, y - 26))
    
    surface.blit(num_surf, num_rect)

# Header--------------------------------------------------------------------------
def draw_game_header(surface, p1_name, p2_name, current_time, score):
    if isinstance(current_time, (int, float)):
        current_time = format_time(current_time)
        
    header_rect = pygame.Rect(0, 0, surface.get_width(), 120)
    pygame.draw.rect(surface, (20, 20, 20), header_rect)
    pygame.draw.line(surface, (80, 80, 80), (0, 120), (surface.get_width(), 120), 4)

    p1_text = font_ui.render(f"{p1_name}", True, (255, 255, 255))
    surface.blit(p1_text, (40, 20))

    p2_text = font_ui.render(f"{p2_name}", True, (255, 0, 0))
    surface.blit(p2_text, (surface.get_width() - p2_text.get_width() - 40, 20))

    center_x = surface.get_width() // 2
    box_w, box_h = 500, 116
    box_rect = pygame.Rect(0, 0, box_w, box_h)
    box_rect.center = (center_x, 60)

    pygame.draw.rect(surface, (30, 30, 45), box_rect, border_radius=16)
    pygame.draw.rect(surface, (100, 100, 130), box_rect, 2, border_radius=16)

    time_surf = word_font.render(f"TIME : {current_time}", True, (255, 215, 0))
    vs_surf = vs_font.render("VS", True, (220, 20, 60))
    score_surf = word_font.render(f"SCORE : {score}", True, (0, 255, 127))

    surface.blit(vs_surf, (center_x - vs_surf.get_width() // 2, box_rect.y + 16))
    surface.blit(time_surf, (box_rect.x + 24, box_rect.y + 22))
    surface.blit(score_surf, (box_rect.right - score_surf.get_width() - 24, box_rect.y + 22))

# Loop-----------------------------------------------------------------------------------
while running:
    current_ticks = pygame.time.get_ticks()

    if paused:
        # Pause state complete freeze adjustment
        pause_duration = pygame.time.get_ticks() - current_ticks
        start_time += pause_duration
        enemy_attack_timer += pause_duration
        susanoo_triger_timer += pause_duration
        if madara_susanoo_active:
            susanoo_start_time += pause_duration

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            W_width, W_height = event.w, event.h
            screen = pygame.display.set_mode((W_width, W_height), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEWHEEL and in_scoreboard:
            target_scroll_offset -= event.y * 90
            max_scroll = max(0, len(scores) * 76 - 400)
            target_scroll_offset = max(0, min(target_scroll_offset, max_scroll))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in (4, 5):
                continue
            win_w, win_h = screen.get_size()
            
            # Letterboxing coordinate mapping for clicks
            virt_w, virt_h = 1600, 1000
            scale = min(win_w / virt_w, win_h / virt_h)
            new_w = int(virt_w * scale)
            new_h = int(virt_h * scale)
            offset_x = (win_w - new_w) // 2
            offset_y = (win_h - new_h) // 2

            if offset_x <= event.pos[0] <= offset_x + new_w and offset_y <= event.pos[1] <= offset_y + new_h:
                virtual_x = int((event.pos[0] - offset_x) / scale)
                virtual_y = int((event.pos[1] - offset_y) / scale)
            else:
                continue

            virtual_mouse_pos = (virtual_x, virtual_y)
            name_box_rect = pygame.Rect(Width // 2 - 600, Height // 2 + 200, 440, 100)
            is_any_btn_clicked = (
                play_btn_rect.collidepoint(virtual_mouse_pos)
                or score_btn_rect.collidepoint(virtual_mouse_pos)
                or exit_btn_rect.collidepoint(virtual_mouse_pos)
                or back_btn_rect.collidepoint(virtual_mouse_pos)
                or reset_btn_rect.collidepoint(virtual_mouse_pos)
                or pause_btn_rect.collidepoint(virtual_mouse_pos)
            )

            if is_any_btn_clicked:
                click_sound.play()
            if in_menu:
                if show_instructions:
                    
                    if close_help_rect and close_help_rect.collidepoint(virtual_mouse_pos):
                        click_sound.play()
                        show_instructions = False
                    elif next_btn_rect and next_btn_rect.collidepoint(virtual_mouse_pos):
                        pageflip_sound.play()
                        instructions_page = (instructions_page + 1) % total_instructions_pages
                    elif prev_btn_rect and prev_btn_rect.collidepoint(virtual_mouse_pos):
                        pageflip_sound.play()
                        instructions_page = (instructions_page - 1 + total_instructions_pages) % total_instructions_pages
                else:
                    if help_btn_rect.collidepoint(virtual_mouse_pos):
                        show_instructions = True
                    elif name_box_rect.collidepoint(virtual_mouse_pos):
                        input_active = True
                    else:
                        input_active = False
                    if play_btn_rect and play_btn_rect.collidepoint(virtual_mouse_pos):
                        if p1_name.strip() == "":
                            p1_name = "PLAYER"
                        in_menu = False
                        reset_game()
                    elif score_btn_rect and score_btn_rect.collidepoint(virtual_mouse_pos):
                        in_menu = False
                        in_scoreboard = True
                    elif exit_btn_rect and exit_btn_rect.collidepoint(virtual_mouse_pos):
                        running = False

            elif paused:
                if back_btn_rect and back_btn_rect.collidepoint(virtual_mouse_pos):
                    paused = False
                    in_menu = True 
                    player1.hp = player1.max_hp
                    player2.hp = player2.max_hp
                    p1_name = ""

            elif not in_menu and not in_scoreboard and not game_over:
                if virtual_x >= Width - 200 and virtual_y <= 120:
                    if pause_btn_rect and pause_btn_rect.collidepoint(virtual_mouse_pos):
                        paused = not paused

            elif in_scoreboard:
                if back_btn_rect and back_btn_rect.collidepoint(virtual_mouse_pos):
                    in_scoreboard = False
                    in_menu = True
                elif reset_btn_rect and reset_btn_rect.collidepoint(virtual_mouse_pos):
                    clear_scores()
                    target_scroll_offset = 0
                    scroll_offset = 0
                else:
                    scores = load_scores()
                    y_offset = 276
                    for i, entry in enumerate(scores):
                        row_y = y_offset + (i * 76) - int(scroll_offset)
                        if 260 <= row_y <= 760:
                            del_btn_rect = pygame.Rect(1230, row_y + 10, 50, 48)
                            if del_btn_rect.collidepoint(virtual_mouse_pos):
                                delete_sound.play()
                                scores.pop(i)
                                with open(SCORE_FILE, "w") as f:
                                    json.dump(scores, f)
                                break
            elif game_over:
                if play_btn_rect and play_btn_rect.collidepoint(virtual_mouse_pos):
                    reset_game()
                    current_word, current_category = get_random_word(score)
                    banner_timer = 0
                    banner_text = "Enjoy"
                elif back_btn_rect and back_btn_rect.collidepoint(virtual_mouse_pos):
                    game_over = False
                    in_menu = True
                    player1.hp = player1.max_hp
                    player2.hp = player2.max_hp
                    p1_name = ""
                    score = 0
                    streak = 0
                    streak_bar_fill = 0.0

        elif event.type == pygame.KEYDOWN:
            if game_over:
                continue
            if not paused:
                last_input_time = pygame.time.get_ticks()
                afk_warning_active = False
                madara_played= False
                key_squeeze_scale = 0.82
                key_sound.play()

            if event.key == pygame.K_ESCAPE:
                if not in_menu and not in_scoreboard and not game_over:
                    paused = not paused
                else:
                    running = False

            elif in_menu and input_active:
                if event.key == pygame.K_BACKSPACE:
                    p1_name = p1_name[:-1]
                elif event.key == pygame.K_RETURN:
                    input_active = False
                else:
                    if event.unicode and len(p1_name) < 10:
                        p1_name += event.unicode.upper()

            elif madara_susanoo_active and not susanoo_defended and not paused:
                if event.unicode:
                    pressed_char = event.unicode.upper()
                    if pressed_char.isalpha() and susanoo_seq_index < len(susanoo_target_sequence):
                        expected_char = susanoo_target_sequence[susanoo_seq_index]
                        if pressed_char == expected_char:
                            susanoo_seq_index += 1
                            if susanoo_seq_index >= len(susanoo_target_sequence):
                                susanoo_defended = True
                        else:
                            susanoo_seq_index = 0

            elif event.key == pygame.K_RETURN and special_attack_active and not paused and not ssj_charging:
                ssj_charging = True
                ssj_charge_timer = ssj_charge_duration
                special_attack_active = False

            elif not in_menu and event.key == pygame.K_SPACE and waiting_for_space and not paused:
                if current_category == "EASY":
                    score += 1
                elif current_category == "MEDIUM":
                    score += 2
                else:
                    score += 3
                typed_index = 0
                waiting_for_space = False
                streak += 1
                if streak > max_game_streak:
                    max_game_streak = streak
                    
                streak_bar_fill = min(100.0, streak_bar_fill + (100.0 / max_streak_for_bar))
                if streak_bar_fill >= 100.0:
                    special_attack_active = True

                if special_word_active:
                    # Jaise hi koi special attack ya word type ho, yeh check karega:
                    if current_special_word == "RED HAWK":
                        red_hawk.play()
                    elif current_special_word == "RASENSHURIKEN":
                        rasenshuriken.play()
                    elif current_special_word == "CHIDORI":
                        chidori.play()
                    elif current_special_word == "BLACK FLASH":
                        blackflash.play()
                    elif current_special_word == "DIMENSION SLASH":
                        dimensionslash.play()
                    elif current_special_word == "AMATERASU":
                        amaterasu.play()
                    elif current_special_word == "KAMEHAMEHA":
                        kamehameha.play()
                    elif current_special_word == "ZANKA NO TACHI":
                        zankanotachi.play()
                    elif current_special_word == "GEAR SHIFT":
                        gearshift.play()
                    elif current_special_word == "FUGA":
                        fuga.play()

                    special_word_active = False 
                    current_special_word = ""
                    normal_word_typed_counter = 0
                    current_word, current_category = get_random_word(score)
                else:
                    normal_word_typed_counter += 1
                    if normal_word_typed_counter >= 10:
                        special_word_active = True
                        current_special_word = random.choice(SPECIAL_WORD_POOL)
                        current_word, current_category = get_random_word(score)
                    else:
                        current_word, current_category = get_random_word(score)

            elif not in_menu and event.key == pygame.K_BACKSPACE and not paused:
                if typed_index > 0:
                    typed_index -= 1

            elif not waiting_for_space and event.unicode and not paused:
                pressed_char = event.unicode.upper()
                active_target_word = current_special_word if special_word_active else current_word

                if pressed_char.isalpha():
                    total_keystrokes += 1

                if typed_index < len(active_target_word) and pressed_char == active_target_word[typed_index]:
                    if boost_active:
                        fireball_sound.play()
                    else:
                        kunai_sound.play()

                    if not timer_started:
                        timer_started = True
                        start_time = pygame.time.get_ticks()
                        susanoo_start_time = pygame.time.get_ticks()
                        susanoo_triger_timer = pygame.time.get_ticks() + 20000

                    correct_keystrokes += 1

                    damage_dealt = 3 if boost_active else 1

                    if not madara_susanoo_active and not special_word_active and player1.hp > 0:
                        player1.start_throw(player2, is_fireball=boost_active)
                    else:
                        player2.take_damage(damage_dealt)

                    typed_index += 1
                else:
                    wrong_key_flash_timer = 24
                    if not special_attack_active:
                        streak = 0
                        streak_bar_fill = 0.0
                        special_attack_active = False

                if typed_index >= len(active_target_word):
                    if special_word_active:
                        player2.take_damage(random.randint(20, 40))
                        player1.hp = min(player1.max_hp, player1.hp + 20)
                    waiting_for_space = True

    if ssj_charging and not paused:
        ssj_sound.play()
        ssj_charge_timer -= 1
        if ssj_charge_timer <= 0:
            ssj_charging = False
            boost_active = True
            boost_timer = pygame.time.get_ticks()
            streak_bar_fill = 0

    if boost_active and not paused:
        if current_ticks - boost_timer > boost_duration:
            boost_active = False

    idle_time = current_ticks - last_input_time
    can_enemy_attack = (timer_started and idle_time < 20000)

# Logic------------------------------------------------------------------------------
    if not in_menu and not game_over and not paused:
        if not game_over:
            if timer_started:
                current_time += dt
            else:
                current_time = 0
        else:
            current_time = frozen_time

        if total_keystrokes > 0:
            accuracy = (correct_keystrokes / total_keystrokes) * 100
        else:
            accuracy = 100.0

        if not game_over and timer_started:
            if special_word_active:
                enemy_attack_cooldown = 2000
            else:
                enemy_attack_cooldown = random.randint(3000, 6000)

            if can_enemy_attack and current_ticks - enemy_attack_timer > enemy_attack_cooldown:
                if not madara_susanoo_active and not special_word_active and player2.hp > 0:
                    enemy_dmg = random.randint(1, 10)
                    player2.start_enemy_attack(player1, enemy_dmg)
                
                enemy_attack_timer = current_ticks

        if not game_over and timer_started:
            if idle_time > 60000:
                player1.hp = 0
            elif idle_time > 40000:
                afk_warning_active = True
            else:
                afk_warning_active = False

        if not game_over and timer_started:
            if madara_susanoo_active:
                if current_ticks - susanoo_start_time > susanoo_duration:
                    madara_susanoo_active = False
                    if not susanoo_defended:
                        player1.hp -= 50
                        slash_anim_timer= 15
                    madara_post_invincibility = True
                    post_invincibility_start_time = current_ticks
                    susanoo_triger_timer = current_ticks
            elif madara_post_invincibility:
                if current_ticks - post_invincibility_start_time > 6000:
                    madara_post_invincibility = False
            else:
                if susanoo_triger_timer == 0:
                    susanoo_triger_timer = current_ticks
                if current_ticks - susanoo_triger_timer > susanoo_cooldown and idle_time < 20000 and not special_word_active:
                    if random.random() < 0.4:
                        madara_susanoo_active = True
                        shake_timer= 360
                        susanoo_scale = 0.0
                        susanoo_start_time = current_ticks
                        susanoo_target_sequence = random.choices(string.ascii_uppercase, k=4)
                        susanoo_seq_index = 0
                        susanoo_defended = False
                        susanoo_triger_timer = current_ticks
                        susanoo_cooldown = random.randint(20000, 30000)

        # Update Stickmans
        player1.update(player2.x)
        player2.update(player1.x)

        if player1.hp <= 0:
            player1.hp = 0
        if player2.hp <= 0:
            player2.hp = 0

# FIXED GAME OVER & SCORE SAVING LOGIC-----------------------------------------------
        if (player1.hp <= 0 or player2.hp <= 0) and not game_over:
            game_over = True
            game_over_alpha = 0
            frozen_time = (pygame.time.get_ticks() - start_time) // 1000
            if player1.hp <= 0 and player2.hp <= 0:
                final_result_text = "IT'S A DRAW"
            elif player1.hp <= 0:
                if idle_time > 60000:
                    final_result_text = "YOU WERE DESTROYED"
                else:
                    final_result_text = "YOU LOSE"

                pathetic.play()
            else:
                final_result_text = "VICTORY"

            if not score_saved:
                save_score(p1_name if p1_name else "PLAYER", score, accuracy, frozen_time)
                scores = load_scores()
                score_saved = True

# Drawing---------------------------------------------------------------------
    virtual_screen.blit(bg_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    win_w, win_h = screen.get_size()
    
    virt_w, virt_h = 1600, 1000
    scale = min(win_w / virt_w, win_h / virt_h)
    new_w = int(virt_w * scale)
    new_h = int(virt_h * scale)
    offset_x = (win_w - new_w) // 2
    offset_y = (win_h - new_h) // 2

    if offset_x <= mouse_pos[0] <= offset_x + new_w and offset_y <= mouse_pos[1] <= offset_y + new_h:
        v_mouse_x = int((mouse_pos[0] - offset_x) / scale)
        v_mouse_y = int((mouse_pos[1] - offset_y) / scale)
    else:
        v_mouse_x, v_mouse_y = -1, -1
    v_mouse_pos = (v_mouse_x, v_mouse_y)

# Main menu-------------------------------------------------------------------------
    name_box_rect = pygame.Rect(Width // 2 - 600, Height // 2 + 200, 200, 40)
    if in_menu:
        virtual_screen.blit(bg_img, (0, 0))
        player1.draw(virtual_screen)
        player2.draw(virtual_screen)

        overlay = pygame.Surface((Width, Height))
        overlay.set_alpha(140)
        overlay.fill((0, 0, 0))
        virtual_screen.blit(overlay, (0, 0))
        logo_rect = logo_img.get_rect(center=(Width // 2, Height // 3 - 80))
        
        virtual_screen.blit(logo_img, logo_rect)
        box_color = (255, 215, 9) if input_active else (100, 100, 100)
        shadow_rect = name_box_rect.copy()
        shadow_rect.y += 8
        pygame.draw.rect(virtual_screen, (15, 15, 20), shadow_rect, border_radius=6)
        pygame.draw.rect(virtual_screen, (30, 30, 50), name_box_rect, border_radius=6)
        pygame.draw.rect(virtual_screen, box_color, name_box_rect, 4, border_radius=6)
        is_cursor_on = (pygame.time.get_ticks() // 400) % 2 == 0
        cursor_str = "|" if (input_active and is_cursor_on) else ""
        if p1_name != "":
            display_name = p1_name + cursor_str
        elif input_active:
            display_name = cursor_str
        else:
            display_name = "Write Name"
        
        text_color = (255, 255, 255) if p1_name else (150, 150, 150)
        name_text_surf = word_font.render(display_name, True, text_color)
        virtual_screen.blit(name_text_surf, name_text_surf.get_rect(center=name_box_rect.center))

        enemy_box_rect = pygame.Rect(Width // 2 + 400, Height // 2 + 200, 200, 40)
        pygame.draw.rect(virtual_screen, (30, 30, 50), enemy_box_rect, border_radius=6)
        pygame.draw.rect(virtual_screen, (220, 20, 60), enemy_box_rect, 4, border_radius=6)

        madara_label = word_font.render("MADARA", True, (220, 20, 60))
        virtual_screen.blit(madara_label, madara_label.get_rect(center=enemy_box_rect.center))

        play_btn_rect = pygame.Rect(Width // 2 - 260, Height // 2 + 120, 520, 100)
        draw_arcade_button(virtual_screen, play_btn_rect, "PLAY", word_font, (30, 30, 50), is_hovered=play_btn_rect.collidepoint(v_mouse_pos))

        score_btn_rect = pygame.Rect(Width // 2 - 260, Height // 2 + 240, 520, 100)
        draw_arcade_button(virtual_screen, score_btn_rect, "SCORECARD", word_font, (30, 50, 30), is_hovered=score_btn_rect.collidepoint(v_mouse_pos))

        exit_btn_rect = pygame.Rect(Width // 2 - 260, Height // 2 + 360, 520, 100)
        draw_arcade_button(virtual_screen, exit_btn_rect, "EXIT", word_font, (50, 30, 30), is_hovered=exit_btn_rect.collidepoint(v_mouse_pos))

        help_btn_rect = pygame.Rect(Width - 120, 40, 80, 80)
        draw_arcade_button(virtual_screen, help_btn_rect, "?", font_ui, (50, 50, 80), is_hovered=help_btn_rect.collidepoint(v_mouse_pos))

        credit_surf = main_font.render(f" Created By: Shivank Upadhyay ", True, (180,180,180))
        virtual_screen.blit(credit_surf, credit_surf.get_rect(center=(Width // 2 - 520,Height // 2 + 480)))


        # How to Play Popup Overlay inside Main Menu
        if show_instructions:
            help_overlay = pygame.Surface((Width, Height))
            help_overlay.set_alpha(200)
            help_overlay.fill((0, 0, 0))
            virtual_screen.blit(help_overlay, (0, 0))

            popup_rect = pygame.Rect(280, 40, Width - 560, Height - 80)
            pygame.draw.rect(virtual_screen, (30, 30, 45), popup_rect, border_radius=30)
            pygame.draw.rect(virtual_screen, (255, 215, 0), popup_rect, 6, border_radius=30)

            help_title = main_font.render("HOW TO PLAY", True, (255, 215, 0))
            virtual_screen.blit(help_title, help_title.get_rect(center=(Width // 2, popup_rect.y + 70)))

            img_box = pygame.Rect(popup_rect.x + 40, popup_rect.y + 40, popup_rect.width - 80, popup_rect.height - 80)
            pygame.draw.rect(virtual_screen, (20, 20, 30), img_box, border_radius=16)
            pygame.draw.rect(virtual_screen, (100, 100, 130), img_box, 4, border_radius=16)

            if 0 <= instructions_page < len(instructions_images):
                current_img = instructions_images[instructions_page]
                img_rect = current_img.get_rect()
                scale_factor = min(img_box.width / img_rect.width, img_box.height / img_rect.height)
                new_width = int(img_rect.width * scale_factor)
                new_height = int(img_rect.height * scale_factor)

                scaled_instruction_img = pygame.transform.scale(current_img, (new_width, new_height))
                img_blit_rect = scaled_instruction_img.get_rect(center=img_box.center)
                virtual_screen.blit(scaled_instruction_img, img_blit_rect)

            prev_btn_rect = pygame.Rect(img_box.x + 40, img_box.centery - 40, 80, 80)
            next_btn_rect = pygame.Rect(img_box.right - 120, img_box.centery - 40, 80, 80)
            draw_arcade_button(virtual_screen, prev_btn_rect, "<", font_ui, (50, 50, 80), is_hovered=prev_btn_rect.collidepoint(v_mouse_pos))
            draw_arcade_button(virtual_screen, next_btn_rect, ">", font_ui, (50, 50, 80), is_hovered=next_btn_rect.collidepoint(v_mouse_pos))

            close_help_rect = pygame.Rect(popup_rect.right - 90, popup_rect.y + 30, 60, 60)
            draw_arcade_button(virtual_screen, close_help_rect, "X", font_ui, (180, 30, 30), is_hovered=close_help_rect.collidepoint(v_mouse_pos))

# Score Board----------------------------------------------------------------------
    elif in_scoreboard:
        virtual_screen.blit(bg_img, (0, 0))
        overlay = pygame.Surface((Width, Height))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        virtual_screen.blit(overlay, (0, 0))

        board_rect = pygame.Rect(360, 90, 960, 860)
        pygame.draw.rect(virtual_screen, (245, 130, 32), board_rect, border_radius=50)
        pygame.draw.rect(virtual_screen, (20, 20, 30), board_rect, 8, border_radius=50)

        title_rect = pygame.Rect(540, 40, 520, 90)
        pygame.draw.rect(virtual_screen, (255, 215, 0), title_rect, border_radius=16)
        pygame.draw.rect(virtual_screen, (20, 20, 30), title_rect, 4, border_radius=16)
        sb_title = font_f2.render("SCOREBOARD", True, (20, 20, 30))
        virtual_screen.blit(sb_title, sb_title.get_rect(center=title_rect.center))

        header_box = pygame.Rect(360, 190, 960, 70)
        pygame.draw.rect(virtual_screen, (30, 90, 100), header_box, border_radius=12)

        name_h = font_ui.render("Name", True, (255, 255, 255))
        score_h = font_ui.render("Score", True, (255, 255, 255))
        accuracy_h = font_ui.render("Accuracy", True, (255, 255, 255))
        time_h = font_ui.render("Time", True, (255, 255, 255))

        virtual_screen.blit(name_h, (400, 206))
        virtual_screen.blit(score_h, (640, 206))
        virtual_screen.blit(accuracy_h, (880, 206))
        virtual_screen.blit(time_h, (1120, 206))

        scores = load_scores()
        y_offset = 276
        scroll_offset += (target_scroll_offset - scroll_offset) * 0.2
        
        if not scores:
            no_score_text = main_font.render("No Records Found!", True, (60, 60, 60))
            virtual_screen.blit(no_score_text, no_score_text.get_rect(center=(Width // 2, 460)))
        else:
            for i, entry in enumerate(scores):
                row_y = y_offset + (i * 76) - int(scroll_offset)
                if 260 <= row_y <= 760:
                    row_rect = pygame.Rect(400, row_y, 880, 68)
                    pygame.draw.rect(virtual_screen, (255, 255, 255), row_rect, border_radius=8)
                    pygame.draw.line(virtual_screen, (40, 40, 40), (400, row_y + 68), (1280, row_y + 68), 2)

                    p_name = name_font.render(str(entry.get('name', 'N/A'))[:10], True, (20, 20, 20))
                    p_score = name_font.render(str(entry.get('score', 0)), True, (20, 20, 20))
                    p_accuracy = name_font.render(str(entry.get('accuracy', 0)), True, (20, 20, 20))
                    p_time = name_font.render(str(entry.get('time', '00:00')), True, (20, 20, 20))

                    virtual_screen.blit(p_name, (400, row_y + 16))
                    virtual_screen.blit(p_score, (660, row_y + 16))
                    virtual_screen.blit(p_accuracy, (920, row_y + 16))
                    virtual_screen.blit(p_time, (1130, row_y + 16))

                    del_btn_rect = pygame.Rect(1230, row_y + 10, 50, 48)
                    is_del_hovered = del_btn_rect.collidepoint(v_mouse_pos)
                    pygame.draw.rect(virtual_screen, (200, 40, 40) if is_del_hovered else (160, 30, 30), del_btn_rect, border_radius=8)
                    del_surf = word_font.render("-", True, (255, 255, 255))
                    virtual_screen.blit(del_surf, del_surf.get_rect(center=del_btn_rect.center))

        reset_btn_rect = pygame.Rect(500, 790, 280, 70)
        draw_arcade_button(virtual_screen, reset_btn_rect, "Reset Records", font_ui, (140, 30, 30), is_hovered=reset_btn_rect.collidepoint(v_mouse_pos))

        back_btn_rect = pygame.Rect(820, 790, 280, 70)
        draw_arcade_button(virtual_screen, back_btn_rect, "Back to Menu", font_ui, (50, 50, 80), is_hovered=back_btn_rect.collidepoint(v_mouse_pos))

# End game-------------------------------------------------------------------------
    elif game_over:
        virtual_screen.blit(bg_img, (0, 0))
        
        # SSJ Aura Behind Player 1 on Game Over screen if active
        if ssj_charging or boost_active:
            cx, cy = int(player1.x), int(player1.y - 70)
            aura_surf = pygame.Surface((220,220), pygame.SRCALPHA)
            num_spikes = 12
            base_radius = 70 + int(math.sin(current_ticks * 0.05) * 8)
            spike_points_outer = []
            spike_points_inner = []
            for i in range(num_spikes):
                angle = (i / num_spikes) * (2 * math.pi)
                r_out = base_radius + random.randint(10, 25) if (i % 2 == 0) else base_radius
                ox = cx + int(math.cos(angle) * r_out * 1.2)
                oy = cy + int(math.sin(angle) * r_out * 2.0)
                spike_points_outer.append((ox, oy))
                r_in = base_radius * 0.6
                ix = cx + int(math.cos(angle) * r_in * 0.7)
                iy = cy + int(math.sin(angle) * r_in * 1.2)
                spike_points_inner.append((ix, iy))
            pygame.draw.polygon(aura_surf, (255, 140, 0, 110), spike_points_outer)
            pygame.draw.polygon(aura_surf, (255, 230, 0, 140), spike_points_inner)
            virtual_screen.blit(aura_surf, (0, 0))

        player1.draw(virtual_screen)
        player2.draw(virtual_screen)
        draw_game_header(virtual_screen, p1_name, p2_name, current_time, score)
        
        # Advanced Healthbars on Game Over screen too
        draw_advanced_health_bar(virtual_screen, 60, 60, player1, is_right_side=False)
        draw_advanced_health_bar(virtual_screen, Width - 420, 60, player2, is_right_side=True)

        if game_over_alpha < 150:
            game_over_alpha += 25

        overlay = pygame.Surface((Width, Height))
        overlay.set_alpha(140)
        overlay.fill((0, 0, 0))
        virtual_screen.blit(overlay, (0, 0))

        # Main Card Panel
        card_rect = pygame.Rect(Width // 2 - 420, Height // 2 - 420, 840, 840)
        pygame.draw.rect(virtual_screen, (25, 25, 35), card_rect, border_radius=28)
        pygame.draw.rect(virtual_screen, (255, 215, 0), card_rect, 4, border_radius=28)

        #  Sabse Upar: Logo
        small_logo = pygame.transform.scale(logo_img, (480, 146))
        logo_rect = small_logo.get_rect(center=(Width // 2, card_rect.y + 90))
        virtual_screen.blit(small_logo, logo_rect)


        #  Uske Niche: Result Text (Victory / Lose)
        result_color = (0, 255, 0) if final_result_text == "VICTORY" else (220, 20, 60)
        result_surf = main_font.render(final_result_text, True, result_color)
        result_rect = result_surf.get_rect(center=(Width // 2, card_rect.y + 200))
        msg_bg_rect = result_rect.inflate(48, 18)
        pygame.draw.rect(virtual_screen, (10, 10, 10), msg_bg_rect, border_radius=8)
        pygame.draw.rect(virtual_screen, result_color, msg_bg_rect, 3, border_radius=8)
        virtual_screen.blit(result_surf, result_rect)

        # Divider Line 1
        pygame.draw.line(virtual_screen, (60, 60, 80), (card_rect.x + 60, card_rect.y + 250), (card_rect.right - 60, card_rect.y + 250), 2)

        #  Stats Section (Score, Time, Accuracy)
        stats_start_y = card_rect.y + 290

        score_surf = main_font.render(f"Final Score : {score}", True, (255, 255, 255))
        virtual_screen.blit(score_surf, score_surf.get_rect(center=(Width // 2, stats_start_y)))

        time_surf = main_font.render(f"Time Taken : {format_time(current_time)}", True, (255, 255, 255))
        virtual_screen.blit(time_surf, time_surf.get_rect(center=(Width // 2, stats_start_y + 70)))

        accuracy_surf = main_font.render(f"Accuracy : {accuracy:.1f}%", True, (0, 255, 255))
        virtual_screen.blit(accuracy_surf, accuracy_surf.get_rect(center=(Width // 2, stats_start_y + 140)))

        # Divider Line 2
        pygame.draw.line(virtual_screen, (60, 60, 80), (card_rect.x + 60, card_rect.y + 490), (card_rect.right - 60, card_rect.y + 490), 2)


        #  Sabse Neeche: Action Buttons
        play_btn_rect = pygame.Rect(Width // 2 - 320, card_rect.bottom - 220, 660, 90)
        draw_arcade_button(virtual_screen, play_btn_rect, "Play Again", font_ui, (30, 120, 50), is_hovered=play_btn_rect.collidepoint(v_mouse_pos))

        back_btn_rect = pygame.Rect(Width // 2 - 320, card_rect.bottom - 120, 660, 90)
        draw_arcade_button(virtual_screen, back_btn_rect, "Back to Menu", font_ui, (50, 50, 80), is_hovered=back_btn_rect.collidepoint(v_mouse_pos))
# Taskbar------------------------------------------------------------------------------
    else:
        # 1. SSJ Goku Charged-up Aura Shape (Spiky Energy Pillars / Flames) BEHIND Player 1
        if ssj_charging or boost_active:
            cx, cy = int(player1.x), int(player1.y - 70)
            aura_surf = pygame.Surface((Width, Height), pygame.SRCALPHA)
            num_spikes = 12
            base_radius = 55 + int(math.sin(current_ticks * 0.05) * 8)
            spike_points_outer = []
            spike_points_inner = []
            
            for i in range(num_spikes):
                angle = (i / num_spikes) * (2 * math.pi)
                r_out = base_radius + random.randint(10, 25) if (i % 2 == 0) else base_radius
                ox = cx + int(math.cos(angle) * r_out * 0.8)
                oy = cy + int(math.sin(angle) * r_out * 1.4)
                spike_points_outer.append((ox, oy))
                
                r_in = base_radius * 0.6
                ix = cx + int(math.cos(angle) * r_in * 0.7)
                iy = cy + int(math.sin(angle) * r_in * 1.2)
                spike_points_inner.append((ix, iy))

            # Draw low opacity aura layers directly onto the alpha surface
            pygame.draw.polygon(aura_surf, (255, 140, 0, 110), spike_points_outer)
            pygame.draw.polygon(aura_surf, (255, 230, 0, 140), spike_points_inner)
            virtual_screen.blit(aura_surf, (0, 0))

        # 2. Draw Player 1 & Player 2 ON TOP of the aura
        player1.draw(virtual_screen)
        player2.draw(virtual_screen)

        if madara_susanoo_active and susanoo_defended:
            shield_center = (int(player1.x), int(player1.y - 70))
            pygame.draw.circle(virtual_screen, (0, 255, 255), shield_center, 120, 4)
            
            shield_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (0, 200, 255, 60), (80, 80), 120)
            virtual_screen.blit(shield_surf, (shield_center[0] - 80, shield_center[1] - 80))


        # 3. Floating energy sparks/particles in front / around player
        if ssj_charging or boost_active:
            cx, cy = int(player1.x), int(player1.y - 70)
            spark_surf = pygame.Surface((Width, Height), pygame.SRCALPHA)
            for _ in range(4):
                px = cx + random.randint(-80, 80)
                py = cy + random.randint(-110, 60)
                spark_color = random.choice([(255, 255, 255, 180), (255, 215, 0, 180), (255, 100, 0, 180)])
                pygame.draw.circle(spark_surf, spark_color, (int(px), int(py)), random.randint(2, 5))
            virtual_screen.blit(spark_surf, (0, 0))

        draw_game_header(virtual_screen, p1_name, p2_name, current_time, score)
        
        # DRAW ADVANCED HEALTHBARS WITH GHOST BAR & ROLLING NUMBERS
        draw_advanced_health_bar(virtual_screen, 60, 60, player1, is_right_side=False)
        draw_advanced_health_bar(virtual_screen, Width - 420, 60, player2, is_right_side=True)

        mouse_near_top_right = (v_mouse_x >= Width - 200 and v_mouse_y <= 120)
        if mouse_near_top_right:
            draw_arcade_button(virtual_screen, pause_btn_rect, "||", font_ui, (60, 60, 80), is_hovered=pause_btn_rect.collidepoint(v_mouse_pos))

        bar_x, bar_y, bar_w, bar_h = 620, 90, 360, 20
        pygame.draw.rect(virtual_screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
        fill_width = int((streak_bar_fill / 100.0) * bar_w)
        
        if boost_active:
            bar_color = (255, 215, 0)
        else:
            bar_color = (0, 255, 255) if not special_attack_active else (255, 215, 0)
            
        if fill_width > 0:
            pygame.draw.rect(virtual_screen, bar_color, (bar_x, bar_y, fill_width, bar_h), border_radius=10)
        pygame.draw.rect(virtual_screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
        
        if special_attack_active and not boost_active and not ssj_charging:
            sp_text = main_font.render("KBOOM! [PRESS ENTER]", True, (255, 215, 0))
            box_bg = sp_text.get_rect(topleft=(bar_x - 100, bar_y + 40)).inflate(24, 12)
            pygame.draw.rect(virtual_screen, (20, 20, 30), box_bg, border_radius=8)
            pygame.draw.rect(virtual_screen, (255, 215, 0), box_bg, 2, border_radius=8)
            virtual_screen.blit(sp_text, (bar_x - 100, bar_y + 40))
        elif ssj_charging:
            charge_text = main_font.render("CHARGING... (SSJ)", True, (255, 255, 0))
            box_bg = charge_text.get_rect(topleft=(bar_x - 60, bar_y + 40)).inflate(24, 12)
            pygame.draw.rect(virtual_screen, (30, 30, 10), box_bg, border_radius=8)
            pygame.draw.rect(virtual_screen, (255, 255, 0), box_bg, 2, border_radius=8)
            virtual_screen.blit(charge_text, (bar_x - 60, bar_y + 40))
        elif boost_active:
            boost_text = main_font.render(">>Damage x 3<<", True, (255, 215, 0))
            box_bg = boost_text.get_rect(topleft=(bar_x + 40, bar_y + 40)).inflate(24, 12)
            pygame.draw.rect(virtual_screen, (20, 20, 30), box_bg, border_radius=8)
            pygame.draw.rect(virtual_screen, (255, 215, 0), box_bg, 2, border_radius=8)
            virtual_screen.blit(boost_text, (bar_x + 40, bar_y + 40))

        if madara_susanoo_active and not susanoo_defended:
            danger_overlay = pygame.Surface((Width, Height))
            danger_overlay.set_alpha(70)
            danger_overlay.fill((180, 0, 0))
            virtual_screen.blit(danger_overlay, (0, 0))

            banner_rect = pygame.Rect(0, 0, 960, 140)
            banner_rect.center = (Width // 2, 200)
            shadow_rect = banner_rect.copy()
            shadow_rect.y += 8
            pygame.draw.rect(virtual_screen, (10, 10, 15), shadow_rect, border_radius=16)
            pygame.draw.rect(virtual_screen, (30, 30, 45), banner_rect, border_radius=16)
            pygame.draw.rect(virtual_screen, (255, 69, 0), banner_rect, 4, border_radius=16)

            font_sus_title = pygame.font.SysFont("impact", 44)
            title_surf = font_sus_title.render("⚠️ WARNING: SUSANOO ONSLAUGHT! ⚠️", True, (255, 215, 0))
            virtual_screen.blit(title_surf, title_surf.get_rect(center=banner_rect.center))

            if susanoo_target_sequence:
                seq_w = len(susanoo_target_sequence) * 88
                seq_box = pygame.Rect(0, 0, seq_w + 80, 130)
                seq_box.center = (Width // 2, 360)

                pygame.draw.rect(virtual_screen, (20, 20, 30, 200), seq_box, border_radius=20)
                pygame.draw.rect(virtual_screen, (0, 255, 255), seq_box, 4, border_radius=20)

                cap_w, cap_h, spacing = 72, 88, 16
                total_w = len(susanoo_target_sequence) * (cap_w + spacing) - spacing
                start_x = seq_box.centerx - (total_w // 2)
                start_y = seq_box.y + 20

                for i, char in enumerate(susanoo_target_sequence):
                    cap_x = start_x + i * (cap_w + spacing)
                    cap_rect = pygame.Rect(cap_x, start_y, cap_w, cap_h)

                    if i < susanoo_seq_index:
                        box_color, border_color = (30, 120, 40), (50, 205, 50)
                    elif i == susanoo_seq_index:
                        box_color, border_color = (150, 40, 40), (255, 215, 0)
                    else:
                        box_color, border_color = (45, 45, 60), (120, 120, 150)

                    pygame.draw.rect(virtual_screen, box_color, cap_rect, border_radius=12)
                    pygame.draw.rect(virtual_screen, border_color, cap_rect, 4, border_radius=12)

                    char_surf = word_font.render(char, True, (255, 255, 255))
                    virtual_screen.blit(char_surf, char_surf.get_rect(center=cap_rect.center))

        elif madara_susanoo_active and susanoo_defended:
            shield_center = (int(player1.x), int(player1.y - 70))
            pygame.draw.circle(virtual_screen, (0, 255, 255), shield_center, 120, 4)
            shield_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (0, 200, 255, 60), (80, 80), 120)
            virtual_screen.blit(shield_surf, (shield_center[0] - 80, shield_center[1] - 80))

        
        else:
            display_word = current_special_word if special_word_active else current_word
            if display_word:
                key_squeeze_scale += (1.0 - key_squeeze_scale) * 0.3

                cap_w = 84
                cap_h = 104
                spacing = 16
                total_w = len(display_word) * (cap_w + spacing) - spacing
                start_x = (Width // 2) - (total_w // 2)
                start_y = 360

                for i, char in enumerate(display_word):
                    cap_x = start_x + i * (cap_w + spacing)
                    cap_rect = pygame.Rect(cap_x, start_y, cap_w, cap_h)

                    current_scale = key_squeeze_scale if i == typed_index else 1.0
                    
                    if i == typed_index and wrong_key_flash_timer > 0:
                        box_color = (180, 30, 30)
                        border_color = (255, 100, 100)
                        wrong_key_flash_timer -= 1
                    else:
                        if i < typed_index:
                            box_color = (30, 100, 40)  
                            border_color = (50, 205, 50)
                        elif i == typed_index:
                            box_color = (40, 70, 110) 
                            border_color = (0, 255, 255)
                        else:
                            box_color = (45, 45, 60)
                            border_color = (100, 120, 150)

                    shadow_rect = cap_rect.copy()
                    shadow_rect.y += int(10 * current_scale)
                    shadow_rect.height = int(cap_h * current_scale)
                    pygame.draw.rect(virtual_screen, (15, 15, 20), shadow_rect, border_radius=16)

                    draw_cap_rect = pygame.Rect(cap_x, (start_y + int(10 * (1.0 - current_scale))), cap_w, int(cap_h * current_scale))
                    pygame.draw.rect(virtual_screen, box_color, draw_cap_rect, border_radius=16)
                    pygame.draw.rect(virtual_screen, border_color, draw_cap_rect, 4, border_radius=16)

                    char_surf = font_f.render(char, True, (255, 255, 255))
                    char_rect = char_surf.get_rect(center=draw_cap_rect.center)
                    virtual_screen.blit(char_surf, char_rect)

        if slash_anim_timer > 0:
            slash_anim_timer -= 1
            pygame.draw.line(virtual_screen, (139,0,0), (1200,200), (400, 800), 12)
            pygame.draw.line(virtual_screen, (0,0,0), (1200, 200), (400, 800), 4)


                    
        if special_word_active:
            virtual_screen.blit(red_fog_surface, (0, 0))

        if waiting_for_space:
            space_msg = "Press Space!"
            msg_surface = font_game.render(space_msg, True, (0, 255, 127))
            msg_rect = msg_surface.get_rect(center=(Width // 2, 520))
            virtual_screen.blit(msg_surface, msg_rect)

        if afk_warning_active and not game_over:


# Sharingan Animation Logic
            if not madara_played:
                madara_dialog.play()
                madara_played = True

            if sharingan_frames:
                frame_index = (pygame.time.get_ticks() // 100) % len(sharingan_frames)
                virtual_screen.blit(sharingan_frames[frame_index], (0, 0))
            else:
                dark_overlay = pygame.Surface((Width, Height))
                dark_overlay.set_alpha(220)
                dark_overlay.fill((0, 0, 0))
                virtual_screen.blit(dark_overlay, (0, 0))

            # Madara Warning Text
            warn_surf = font_game.render("Wake up to reality...", True, (255, 0, 0))
            warn_rect = warn_surf.get_rect(center=(Width // 2, Height // 3 - 80))
            warn_bg_rect = warn_rect.inflate(48, 24)
            pygame.draw.rect(virtual_screen, (20, 20, 20), warn_bg_rect, border_radius=4)
            pygame.draw.rect(virtual_screen, (255, 0, 0), warn_bg_rect, 2, border_radius=4)
            virtual_screen.blit(warn_surf, warn_rect)

    if not in_menu and banner_timer > 0 and not paused:
        if banner_scale < 1.0:
            banner_scale += 0.15
            if banner_scale > 1.0:
                banner_scale = 1.0
        banner_surface = font_banner.render(banner_text, True, (220, 20, 60))
        scaled_w = int(banner_surface.get_width() * banner_scale)
        scaled_h = int(banner_surface.get_height() * banner_scale)

        if scaled_w > 0 and scaled_h > 0:
            popped_surface = pygame.transform.scale(banner_surface, (scaled_w, scaled_h))
            banner_rect = popped_surface.get_rect(center=(Width // 2, Height // 2 - 100))
            bg_rect = banner_rect.inflate(80, 40)
            pygame.draw.rect(virtual_screen, (40, 40, 40), bg_rect)
            pygame.draw.rect(virtual_screen, (255, 215, 0), bg_rect, 6)
            virtual_screen.blit(popped_surface, banner_rect)
        banner_timer -= 1
    else:
        banner_scale = 0.0
        
    if banner_timer == 0 and banner_text in ["Victory", "You Lose", "Its A Draw"]:
        game_over = True

    if paused:
        paused_overlay = pygame.Surface((Width, Height))
        paused_overlay.set_alpha(150)
        paused_overlay.fill((0, 0, 0))
        virtual_screen.blit(paused_overlay, (0, 0))

        pause_surf = font_game.render("Game Paused", True, (255, 215, 0))
        virtual_screen.blit(pause_surf, pause_surf.get_rect(center=(Width // 2, Height // 2 - 40)))

        back_btn_rect = pygame.Rect(Width // 2 - 280, Height // 2 + 240, 560, 90)
        draw_arcade_button(virtual_screen, back_btn_rect, "Back to Menu", font_ui, (50, 50, 80), is_hovered=back_btn_rect.collidepoint(v_mouse_pos))

    # Display with HD Letterboxing
    current_window_width, current_window_height = screen.get_size()
    
    scale = min(current_window_width / virt_w, current_window_height / virt_h)
    new_w = int(virt_w * scale)
    new_h = int(virt_h * scale)
    
    offset_x = (current_window_width - new_w) // 2
    offset_y = (current_window_height - new_h) // 2

    screen.fill((10, 10, 15)) 

    scaled_surface = pygame.transform.smoothscale(virtual_screen, (new_w, new_h))

    shake_offset_x = random.randint(-8, 8) if shake_timer > 0 else 0
    shake_offset_y = random.randint(-8, 8) if shake_timer > 0 else 0
    if shake_timer > 0:
        shake_timer -= 1
    screen.blit(scaled_surface, (offset_x + shake_offset_x, offset_y + shake_offset_y))

    pygame.display.flip()
    dt = clock.tick(60) / 1000.0 if not paused else 0.0

# Exit
pygame.quit()
sys.exit()