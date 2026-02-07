#!/usr/bin/env python3
"""
STEAMED HAMS: THE GAME
An NES-style platformer based on the classic Simpsons skit.
Inspired by "Steamed Hams, but it's an NES game from 1991" by Fictional Bad Games.

Controls:
  Arrow Keys - Move
  Z / Space  - Jump
  X / Enter  - Advance dialogue / Interact
  Escape     - Quit
"""

import pygame
import sys
import math
import random
import array

# ============================================================
# CONSTANTS
# ============================================================
NES_W, NES_H = 256, 240
SCALE = 3
WIN_W, WIN_H = NES_W * SCALE, NES_H * SCALE
FPS = 60
GRAVITY = 0.28
JUMP_VEL = -6.5
PLAYER_SPEED = 1.8
TILE = 16
HUD_H = 40  # pixels for HUD at bottom
PLAY_H = NES_H - HUD_H  # playable area height

# ============================================================
# NES COLOR PALETTE
# ============================================================
C_BLACK = (0, 0, 0)
C_WHITE = (252, 252, 252)
C_YELLOW = (252, 212, 56)
C_SKIN = (252, 188, 60)
C_BLUE = (0, 0, 168)
C_LBLUE = (0, 88, 248)
C_SKYBLUE = (104, 136, 252)
C_GRAY = (188, 188, 188)
C_DGRAY = (124, 124, 124)
C_LGRAY = (228, 228, 228)
C_PURPLE = (148, 0, 211)
C_LAVENDER = (152, 120, 248)
C_LPURPLE = (188, 160, 248)
C_MAUVE = (200, 168, 255)
C_PINK = (248, 120, 248)
C_MAGENTA = (216, 0, 204)
C_GREEN = (0, 168, 0)
C_DGREEN = (0, 120, 0)
C_LGREEN = (184, 248, 24)
C_RED = (168, 16, 0)
C_LRED = (248, 56, 0)
C_ORANGE = (248, 120, 0)
C_BROWN = (120, 56, 0)
C_DBROWN = (80, 40, 0)
C_CYAN = (0, 168, 168)
C_TEAL = (0, 120, 136)
C_DRED = (120, 0, 0)
C_CREAM = (252, 228, 160)
C_FIRE_Y = (252, 216, 0)
C_FIRE_O = (248, 120, 0)
C_FIRE_R = (228, 56, 0)


# ============================================================
# SOUND GENERATION
# ============================================================
def generate_square_wave(frequency, duration_ms, volume=0.15):
    """Generate a square wave sound (NES-style)."""
    sample_rate = 22050
    n_samples = int(sample_rate * duration_ms / 1000)
    period = int(sample_rate / frequency) if frequency > 0 else 1
    buf = array.array('h')
    amplitude = int(32767 * volume)
    for i in range(n_samples):
        val = amplitude if (i % period) < (period // 2) else -amplitude
        buf.append(val)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def init_sounds():
    """Create NES-style sound effects."""
    sounds = {}
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        sounds["jump"] = generate_square_wave(440, 80, 0.1)
        sounds["collect"] = generate_square_wave(880, 60, 0.1)
        sounds["hurt"] = generate_square_wave(200, 150, 0.1)
        sounds["stomp"] = generate_square_wave(330, 50, 0.1)
        sounds["text"] = generate_square_wave(660, 20, 0.05)
        # Collect jingle: two notes
        s1 = generate_square_wave(523, 80, 0.1)  # C
        s2 = generate_square_wave(784, 120, 0.1)  # G
        sounds["collect_hi"] = s2
    except Exception:
        pass
    return sounds


# ============================================================
# SPRITE DRAWING FUNCTIONS
# ============================================================
def create_skinner_sprite(facing_right=True, frame=0):
    """Create a 16x28 pixel Skinner sprite."""
    s = pygame.Surface((16, 28), pygame.SRCALPHA)
    # Hair (gray)
    pygame.draw.rect(s, C_GRAY, (4, 0, 8, 6))
    pygame.draw.rect(s, C_DGRAY, (3, 2, 2, 3))
    pygame.draw.rect(s, C_DGRAY, (11, 2, 2, 3))
    # Face
    pygame.draw.rect(s, C_YELLOW, (4, 6, 8, 7))
    # Nose
    if facing_right:
        pygame.draw.rect(s, C_YELLOW, (12, 8, 2, 3))
    else:
        pygame.draw.rect(s, C_YELLOW, (2, 8, 2, 3))
    # Eyes
    if facing_right:
        pygame.draw.rect(s, C_WHITE, (6, 7, 3, 3))
        pygame.draw.rect(s, C_WHITE, (10, 7, 3, 3))
        pygame.draw.rect(s, C_BLACK, (8, 8, 1, 1))
        pygame.draw.rect(s, C_BLACK, (12, 8, 1, 1))
    else:
        pygame.draw.rect(s, C_WHITE, (3, 7, 3, 3))
        pygame.draw.rect(s, C_WHITE, (7, 7, 3, 3))
        pygame.draw.rect(s, C_BLACK, (3, 8, 1, 1))
        pygame.draw.rect(s, C_BLACK, (7, 8, 1, 1))
    # Mouth
    pygame.draw.rect(s, C_BROWN, (6, 11, 4, 1))
    # Suit jacket (blue)
    pygame.draw.rect(s, C_BLUE, (3, 13, 10, 7))
    # White shirt/collar
    pygame.draw.rect(s, C_WHITE, (6, 13, 4, 2))
    # Tie (orange)
    pygame.draw.rect(s, C_ORANGE, (7, 14, 2, 5))
    # Arms
    arm_offset = (1 if frame % 2 == 0 else 0)
    pygame.draw.rect(s, C_BLUE, (1, 14, 3, 5))
    pygame.draw.rect(s, C_BLUE, (12, 14, 3, 5))
    # Hands
    pygame.draw.rect(s, C_YELLOW, (1, 19 + arm_offset, 2, 2))
    pygame.draw.rect(s, C_YELLOW, (13, 19, 2, 2))
    # Pants
    pygame.draw.rect(s, C_BLUE, (4, 20, 4, 5))
    pygame.draw.rect(s, C_BLUE, (8, 20, 4, 5))
    # Leg animation
    if frame % 4 < 2:
        pygame.draw.rect(s, C_BLUE, (4, 20, 4, 5))
        pygame.draw.rect(s, C_BLUE, (8, 20, 4, 5))
    else:
        pygame.draw.rect(s, C_BLUE, (3, 20, 4, 5))
        pygame.draw.rect(s, C_BLUE, (9, 20, 4, 5))
    # Shoes
    pygame.draw.rect(s, C_DGRAY, (3, 25, 5, 3))
    pygame.draw.rect(s, C_DGRAY, (8, 25, 5, 3))
    if not facing_right:
        s = pygame.transform.flip(s, True, False)
    return s


def create_chalmers_sprite(facing_right=True, frame=0):
    """Create a 16x28 pixel Chalmers sprite."""
    s = pygame.Surface((16, 28), pygame.SRCALPHA)
    # Bald head (yellow skin)
    pygame.draw.rect(s, C_YELLOW, (4, 0, 8, 6))
    # Side hair tufts (white)
    pygame.draw.rect(s, C_WHITE, (3, 3, 2, 3))
    pygame.draw.rect(s, C_WHITE, (11, 3, 2, 3))
    # Face
    pygame.draw.rect(s, C_YELLOW, (4, 6, 8, 7))
    # Big nose
    if facing_right:
        pygame.draw.rect(s, C_YELLOW, (12, 7, 3, 4))
    else:
        pygame.draw.rect(s, C_YELLOW, (1, 7, 3, 4))
    # Eyes
    pygame.draw.rect(s, C_WHITE, (5, 7, 3, 3))
    pygame.draw.rect(s, C_WHITE, (9, 7, 3, 3))
    pygame.draw.rect(s, C_BLACK, (7, 8, 1, 1))
    pygame.draw.rect(s, C_BLACK, (11, 8, 1, 1))
    # Mouth
    pygame.draw.rect(s, C_BROWN, (6, 11, 5, 1))
    # Suit (blue)
    pygame.draw.rect(s, C_BLUE, (3, 13, 10, 7))
    # White shirt
    pygame.draw.rect(s, C_WHITE, (6, 13, 4, 2))
    # Tie
    pygame.draw.rect(s, C_ORANGE, (7, 14, 2, 5))
    # Arms
    pygame.draw.rect(s, C_BLUE, (1, 14, 3, 5))
    pygame.draw.rect(s, C_BLUE, (12, 14, 3, 5))
    pygame.draw.rect(s, C_YELLOW, (1, 19, 2, 2))
    pygame.draw.rect(s, C_YELLOW, (13, 19, 2, 2))
    # Pants
    pygame.draw.rect(s, C_BLUE, (4, 20, 4, 5))
    pygame.draw.rect(s, C_BLUE, (8, 20, 4, 5))
    # Shoes
    pygame.draw.rect(s, C_DGRAY, (3, 25, 5, 3))
    pygame.draw.rect(s, C_DGRAY, (8, 25, 5, 3))
    if not facing_right:
        s = pygame.transform.flip(s, True, False)
    return s


def create_agnes_sprite(facing_right=True, frame=0):
    """Create Agnes Skinner sprite."""
    s = pygame.Surface((14, 26), pygame.SRCALPHA)
    # Hair bun (gray)
    pygame.draw.rect(s, C_LGRAY, (4, 0, 6, 4))
    pygame.draw.rect(s, C_LGRAY, (5, 0, 4, 2))
    # Face
    pygame.draw.rect(s, C_YELLOW, (4, 4, 6, 6))
    # Eyes
    pygame.draw.rect(s, C_BLACK, (5, 5, 1, 1))
    pygame.draw.rect(s, C_BLACK, (8, 5, 1, 1))
    # Glasses
    pygame.draw.rect(s, C_DGRAY, (4, 5, 3, 2))
    pygame.draw.rect(s, C_DGRAY, (7, 5, 3, 2))
    # Mouth
    pygame.draw.rect(s, C_BROWN, (5, 8, 4, 1))
    # Dress (purple)
    pygame.draw.rect(s, C_PURPLE, (3, 10, 8, 10))
    # Arms
    pygame.draw.rect(s, C_PURPLE, (1, 11, 3, 5))
    pygame.draw.rect(s, C_PURPLE, (10, 11, 3, 5))
    pygame.draw.rect(s, C_YELLOW, (1, 16, 2, 2))
    pygame.draw.rect(s, C_YELLOW, (11, 16, 2, 2))
    # Legs
    pygame.draw.rect(s, C_PURPLE, (4, 20, 3, 4))
    pygame.draw.rect(s, C_PURPLE, (7, 20, 3, 4))
    # Shoes
    pygame.draw.rect(s, C_DGRAY, (3, 23, 4, 3))
    pygame.draw.rect(s, C_DGRAY, (7, 23, 4, 3))
    if not facing_right:
        s = pygame.transform.flip(s, True, False)
    return s


def create_spider_sprite(frame=0):
    """Create an 10x8 spider enemy."""
    s = pygame.Surface((10, 8), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(s, C_RED, (3, 1, 4, 4))
    pygame.draw.rect(s, C_DRED, (4, 0, 2, 1))
    # Eyes
    pygame.draw.rect(s, C_WHITE, (3, 1, 2, 1))
    pygame.draw.rect(s, C_WHITE, (5, 1, 2, 1))
    # Legs (animated)
    if frame % 2 == 0:
        pygame.draw.rect(s, C_RED, (0, 2, 3, 1))
        pygame.draw.rect(s, C_RED, (7, 2, 3, 1))
        pygame.draw.rect(s, C_RED, (1, 4, 2, 1))
        pygame.draw.rect(s, C_RED, (7, 4, 2, 1))
        pygame.draw.rect(s, C_RED, (0, 6, 3, 1))
        pygame.draw.rect(s, C_RED, (7, 6, 3, 1))
        pygame.draw.rect(s, C_RED, (1, 7, 2, 1))
        pygame.draw.rect(s, C_RED, (7, 7, 2, 1))
    else:
        pygame.draw.rect(s, C_RED, (1, 1, 2, 1))
        pygame.draw.rect(s, C_RED, (7, 1, 2, 1))
        pygame.draw.rect(s, C_RED, (0, 3, 3, 1))
        pygame.draw.rect(s, C_RED, (7, 3, 3, 1))
        pygame.draw.rect(s, C_RED, (1, 5, 2, 1))
        pygame.draw.rect(s, C_RED, (7, 5, 2, 1))
        pygame.draw.rect(s, C_RED, (0, 7, 3, 1))
        pygame.draw.rect(s, C_RED, (7, 7, 3, 1))
    return s


def draw_hamburger(surf, x, y, size=12):
    """Draw a hamburger icon."""
    # Top bun
    pygame.draw.rect(surf, C_ORANGE, (x + 1, y, size - 2, 3))
    pygame.draw.rect(surf, C_ORANGE, (x, y + 2, size, 2))
    # Sesame seeds
    pygame.draw.rect(surf, C_CREAM, (x + 3, y + 1, 1, 1))
    pygame.draw.rect(surf, C_CREAM, (x + 7, y + 1, 1, 1))
    # Lettuce
    pygame.draw.rect(surf, C_GREEN, (x, y + 4, size, 2))
    # Patty
    pygame.draw.rect(surf, C_BROWN, (x + 1, y + 6, size - 2, 3))
    # Bottom bun
    pygame.draw.rect(surf, C_ORANGE, (x, y + 9, size, 2))
    pygame.draw.rect(surf, C_ORANGE, (x + 1, y + 11, size - 2, 1))


def draw_key(surf, x, y):
    """Draw a key icon."""
    pygame.draw.rect(surf, C_FIRE_Y, (x, y + 2, 4, 2))
    pygame.draw.rect(surf, C_FIRE_Y, (x + 4, y, 2, 6))
    pygame.draw.rect(surf, C_FIRE_Y, (x + 6, y + 2, 6, 2))
    pygame.draw.rect(surf, C_FIRE_Y, (x + 10, y + 4, 2, 2))
    pygame.draw.rect(surf, C_FIRE_Y, (x + 7, y + 4, 2, 2))


def draw_apron(surf, x, y):
    """Draw an apron icon."""
    pygame.draw.rect(surf, C_WHITE, (x + 2, y, 8, 2))
    pygame.draw.rect(surf, C_WHITE, (x, y + 2, 12, 10))
    pygame.draw.rect(surf, C_WHITE, (x + 2, y + 12, 8, 2))
    pygame.draw.rect(surf, C_LGRAY, (x + 4, y + 4, 4, 4))


def draw_wine_bottle(surf, x, y):
    """Draw a wine bottle icon."""
    pygame.draw.rect(surf, C_LBLUE, (x + 4, y, 2, 3))
    pygame.draw.rect(surf, C_LBLUE, (x + 3, y + 3, 4, 2))
    pygame.draw.rect(surf, C_LBLUE, (x + 2, y + 5, 6, 8))
    pygame.draw.rect(surf, C_LBLUE, (x + 3, y + 13, 4, 1))


def draw_spray_can(surf, x, y):
    """Draw a spray can icon."""
    pygame.draw.rect(surf, C_DGRAY, (x + 3, y, 4, 3))
    pygame.draw.rect(surf, C_LGREEN, (x + 2, y + 3, 6, 9))
    pygame.draw.rect(surf, C_GREEN, (x + 2, y + 8, 6, 4))


def draw_fire(surf, x, y, frame=0):
    """Draw animated fire."""
    off = frame % 4
    colors = [C_FIRE_Y, C_FIRE_O, C_FIRE_R]
    for i in range(3):
        fx = x + random.randint(-1, 1) + (off % 2)
        fy = y - i * 3 - random.randint(0, 2)
        c = colors[i % len(colors)]
        pygame.draw.rect(surf, c, (fx, fy, 4 + random.randint(0, 2), 3))


def draw_graduation_cap(surf, x, y):
    """Draw a small graduation cap (life icon)."""
    pygame.draw.rect(surf, C_LBLUE, (x, y + 2, 9, 3))
    pygame.draw.rect(surf, C_LBLUE, (x + 2, y, 5, 3))
    pygame.draw.rect(surf, C_FIRE_Y, (x + 6, y + 3, 1, 3))


# ============================================================
# DECORATION DRAWING
# ============================================================
def draw_bookshelf(surf, x, y, cam_x=0):
    """Draw a bookshelf decoration."""
    bx = x - cam_x
    # Frame
    pygame.draw.rect(surf, C_BROWN, (bx, y, 32, 72))
    # Shelves
    for sy in range(3):
        shelf_y = y + 4 + sy * 24
        pygame.draw.rect(surf, C_DBROWN, (bx + 2, shelf_y + 20, 28, 3))
        # Books
        for bk in range(5):
            book_c = [C_CYAN, C_LBLUE, C_TEAL, C_GREEN, C_BLUE][bk % 5]
            pygame.draw.rect(surf, book_c, (bx + 3 + bk * 5, shelf_y, 4, 19))


def draw_couch(surf, x, y, cam_x=0):
    """Draw a green couch."""
    cx = x - cam_x
    pygame.draw.rect(surf, C_DGREEN, (cx, y, 40, 24))
    pygame.draw.rect(surf, C_GREEN, (cx + 2, y + 2, 36, 12))
    pygame.draw.rect(surf, C_GREEN, (cx + 2, y + 14, 36, 8))
    # Cushion lines
    pygame.draw.rect(surf, C_DGREEN, (cx + 14, y + 14, 1, 8))
    pygame.draw.rect(surf, C_DGREEN, (cx + 26, y + 14, 1, 8))
    # Arms
    pygame.draw.rect(surf, C_DGREEN, (cx - 2, y + 4, 4, 20))
    pygame.draw.rect(surf, C_DGREEN, (cx + 38, y + 4, 4, 20))


def draw_table(surf, x, y, cam_x=0):
    """Draw a small table."""
    tx = x - cam_x
    pygame.draw.rect(surf, C_BROWN, (tx, y, 20, 3))
    pygame.draw.rect(surf, C_BROWN, (tx + 2, y + 3, 2, 16))
    pygame.draw.rect(surf, C_BROWN, (tx + 16, y + 3, 2, 16))


def draw_door(surf, x, y, cam_x=0, color=C_BLUE):
    """Draw a door."""
    dx = x - cam_x
    pygame.draw.rect(surf, color, (dx, y, 20, 40))
    pygame.draw.rect(surf, C_DGRAY, (dx + 1, y + 1, 18, 38))
    pygame.draw.rect(surf, color, (dx + 3, y + 3, 14, 16))
    pygame.draw.rect(surf, color, (dx + 3, y + 21, 14, 16))
    # Knob
    pygame.draw.rect(surf, C_FIRE_Y, (dx + 14, y + 20, 3, 3))


def draw_lockers(surf, x, y, cam_x=0, count=6):
    """Draw school lockers."""
    lx = x - cam_x
    total_w = count * 12
    pygame.draw.rect(surf, C_GRAY, (lx, y, total_w, 48))
    for i in range(count):
        ix = lx + i * 12
        pygame.draw.rect(surf, C_DGRAY, (ix, y, 1, 48))
        pygame.draw.rect(surf, C_LGRAY, (ix + 2, y + 4, 8, 8))
        pygame.draw.rect(surf, C_LGRAY, (ix + 2, y + 14, 8, 30))
        pygame.draw.rect(surf, C_BLACK, (ix + 5, y + 28, 2, 2))


def draw_clock(surf, x, y, cam_x=0):
    """Draw a wall clock."""
    cx = x - cam_x
    pygame.draw.ellipse(surf, C_WHITE, (cx, y, 14, 14))
    pygame.draw.ellipse(surf, C_BLACK, (cx, y, 14, 14), 1)
    pygame.draw.rect(surf, C_BLACK, (cx + 6, y + 3, 1, 5))
    pygame.draw.rect(surf, C_BLACK, (cx + 6, y + 6, 4, 1))


def draw_water_fountain(surf, x, y, cam_x=0):
    """Draw a water fountain."""
    fx = x - cam_x
    pygame.draw.rect(surf, C_GRAY, (fx, y, 10, 20))
    pygame.draw.rect(surf, C_LGRAY, (fx - 2, y, 14, 6))
    pygame.draw.rect(surf, C_LBLUE, (fx + 2, y + 1, 6, 3))


# ============================================================
# ENTITY CLASSES
# ============================================================
class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 14, 28
        self.facing_right = True
        self.on_ground = False
        self.health = 3
        self.max_health = 3
        self.lives = 4
        self.score = 0
        self.inventory = []
        self.goals_done = 0
        self.anim_frame = 0
        self.anim_timer = 0
        self.invuln_timer = 0
        self.current_item_name = ""
        self.current_item_icon = None  # draw function
        self._jump_sound = False
        self._hurt_sound = False
        self._collect_sound = False

    def update(self, keys, platforms, level_width):
        # Horizontal movement
        self.vx = 0
        if keys[pygame.K_LEFT]:
            self.vx = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vx = PLAYER_SPEED
            self.facing_right = True

        # Jump
        if (keys[pygame.K_z] or keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False
            self._jump_sound = True

        # Gravity
        self.vy += GRAVITY
        if self.vy > 7:
            self.vy = 7

        # Move X
        self.x += self.vx
        self.x = max(0, min(self.x, level_width - self.w))

        # Move Y
        old_bottom = self.y + self.h
        self.y += self.vy
        self.on_ground = False
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        for plat in platforms:
            if rect.colliderect(plat.rect):
                if self.vy > 0 and old_bottom <= plat.rect.top + 2:
                    # One-way platform: land on top only when falling from above
                    self.y = plat.rect.top - self.h
                    self.vy = 0
                    self.on_ground = True
                rect = pygame.Rect(self.x, self.y, self.w, self.h)

        # Fall off bottom
        if self.y > PLAY_H + 20:
            self.take_damage(1)
            self.y = 20
            self.vy = 0

        # Animation
        if abs(self.vx) > 0.1:
            self.anim_timer += 1
            if self.anim_timer > 8:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0
            self.anim_timer = 0

        # Invulnerability timer
        if self.invuln_timer > 0:
            self.invuln_timer -= 1

    def take_damage(self, amount):
        if self.invuln_timer > 0:
            return
        self.health -= amount
        self.invuln_timer = 60
        self._hurt_sound = True
        if self.health <= 0:
            self.lives -= 1
            self.health = self.max_health
            if self.lives < 0:
                self.lives = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf, cam_x=0):
        if self.invuln_timer > 0 and self.invuln_timer % 4 < 2:
            return  # Blink when invulnerable
        sprite = create_skinner_sprite(self.facing_right, self.anim_frame)
        surf.blit(sprite, (int(self.x - cam_x), int(self.y)))


class Enemy:
    def __init__(self, x, y, enemy_type="spider", patrol_left=0, patrol_right=200):
        self.x, self.y = float(x), float(y)
        self.vx = 0.5
        self.vy = 0
        self.enemy_type = enemy_type
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.alive = True
        self.anim_frame = 0
        self.anim_timer = 0
        self.bounce_vy = 0
        if enemy_type == "spider":
            self.w, self.h = 10, 8
            self.bounce_vy = -2  # spiders bounce

    def update(self, platforms):
        # Patrol horizontally
        self.x += self.vx
        if self.x <= self.patrol_left or self.x >= self.patrol_right:
            self.vx = -self.vx

        # Vertical bounce for spiders
        if self.enemy_type == "spider":
            self.vy += GRAVITY * 0.5
            self.y += self.vy
            for plat in platforms:
                if pygame.Rect(self.x, self.y, self.w, self.h).colliderect(plat.rect):
                    if self.vy > 0:
                        self.y = plat.rect.top - self.h
                        self.vy = self.bounce_vy
            if self.y > PLAY_H:
                self.y = 20
                self.vy = 0

        # Animation
        self.anim_timer += 1
        if self.anim_timer > 10:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 2

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf, cam_x=0):
        if not self.alive:
            return
        if self.enemy_type == "spider":
            sprite = create_spider_sprite(self.anim_frame)
            surf.blit(sprite, (int(self.x - cam_x), int(self.y)))


class Collectible:
    def __init__(self, x, y, item_type, name):
        self.x, self.y = x, y
        self.item_type = item_type
        self.name = name
        self.collected = False
        self.bob_offset = random.random() * 6.28
        self.w, self.h = 12, 12

    @property
    def rect(self):
        y_off = int(math.sin(pygame.time.get_ticks() * 0.003 + self.bob_offset) * 2)
        return pygame.Rect(self.x, self.y + y_off, self.w, self.h)

    def draw(self, surf, cam_x=0):
        if self.collected:
            return
        y_off = int(math.sin(pygame.time.get_ticks() * 0.003 + self.bob_offset) * 2)
        dx = int(self.x - cam_x)
        dy = int(self.y + y_off)
        if self.item_type == "hamburger":
            draw_hamburger(surf, dx, dy)
        elif self.item_type == "key":
            draw_key(surf, dx, dy)
        elif self.item_type == "apron":
            draw_apron(surf, dx, dy)
        elif self.item_type == "wine":
            draw_wine_bottle(surf, dx, dy)
        elif self.item_type == "spray_can":
            draw_spray_can(surf, dx, dy)
        else:
            # Generic pickup
            pygame.draw.rect(surf, C_FIRE_Y, (dx, dy, 10, 10))
            pygame.draw.rect(surf, C_WHITE, (dx + 2, dy + 2, 6, 6))


class NPC:
    def __init__(self, x, y, npc_type, patrol_left=None, patrol_right=None):
        self.x, self.y = float(x), float(y)
        self.npc_type = npc_type
        self.vx = 0.3 if patrol_left is not None else 0
        self.patrol_left = patrol_left or x
        self.patrol_right = patrol_right or x
        self.facing_right = True
        self.anim_frame = 0
        self.anim_timer = 0

    def update(self):
        if self.vx != 0:
            self.x += self.vx
            if self.x <= self.patrol_left:
                self.vx = abs(self.vx)
                self.facing_right = True
            elif self.x >= self.patrol_right:
                self.vx = -abs(self.vx)
                self.facing_right = False
        self.anim_timer += 1
        if self.anim_timer > 12:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, surf, cam_x=0):
        dx = int(self.x - cam_x)
        dy = int(self.y)
        if self.npc_type == "agnes":
            sprite = create_agnes_sprite(self.facing_right, self.anim_frame)
            surf.blit(sprite, (dx, dy))
        elif self.npc_type == "chalmers":
            sprite = create_chalmers_sprite(self.facing_right, self.anim_frame)
            surf.blit(sprite, (dx, dy))
        elif self.npc_type == "student":
            # Generic blue-suited character
            sprite = create_chalmers_sprite(self.facing_right, self.anim_frame)
            surf.blit(sprite, (dx, dy))
        elif self.npc_type == "lunch_lady":
            sprite = create_agnes_sprite(self.facing_right, self.anim_frame)
            surf.blit(sprite, (dx, dy))


class Platform:
    def __init__(self, x, y, w, h, color=C_BROWN, visible=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.visible = visible

    def draw(self, surf, cam_x=0):
        if not self.visible:
            return
        r = self.rect.move(-cam_x, 0)
        pygame.draw.rect(surf, self.color, r)


class FireHazard:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 12, 16
        self.frame = random.randint(0, 100)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf, cam_x=0):
        self.frame += 1
        dx = int(self.x - cam_x)
        dy = int(self.y)
        for i in range(3):
            c = [C_FIRE_Y, C_FIRE_O, C_FIRE_R][i]
            ox = (self.frame // 3 + i * 2) % 4 - 2
            oy = -i * 4
            pygame.draw.rect(surf, c, (dx + 2 + ox, dy + 8 + oy, 6, 6))
        pygame.draw.rect(surf, C_FIRE_Y, (dx + 3, dy + 2, 4, 8))
        pygame.draw.rect(surf, C_FIRE_O, (dx + 2, dy + 6, 8, 8))


# ============================================================
# LEVEL DEFINITIONS
# ============================================================
def create_level_house():
    """Level 1: Skinner's House - collect apron and kitchen key."""
    # With JUMP_VEL=-6.5, GRAVITY=0.28: max jump = 75px, so from floor
    # (player at y=164) bottom at apex = 116.6. Can land on platforms y>=117.
    platforms = [
        Platform(0, PLAY_H - 8, 512, 16, C_PINK),     # floor
        # Stepping ledges
        Platform(65, PLAY_H - 36, 24, 6, C_BROWN),     # table top
        Platform(378, PLAY_H - 32, 6, 24, C_DGREEN),   # couch arm
        # Shelves - all reachable from floor (y >= 120)
        Platform(90, PLAY_H - 60, 56, 6, C_ORANGE),    # shelf 1
        Platform(210, PLAY_H - 65, 56, 6, C_ORANGE),   # shelf 2
        Platform(340, PLAY_H - 60, 48, 6, C_ORANGE),   # shelf 3
        # Bookshelf tops
        Platform(145, PLAY_H - 72, 30, 4, C_BROWN, visible=False),
        Platform(280, PLAY_H - 72, 30, 4, C_BROWN, visible=False),
    ]
    enemies = [
        Enemy(180, 80, "spider", 100, 350),
        Enemy(380, 100, "spider", 320, 480),
    ]
    items = [
        Collectible(105, PLAY_H - 76, "apron", "APRON"),
        Collectible(350, PLAY_H - 76, "key", "KITCHEN KEY"),
    ]
    npcs = [
        NPC(300, PLAY_H - 34, "agnes", 250, 400),
    ]
    return {
        "width": 512,
        "bg_color": C_LAVENDER,
        "floor_y": PLAY_H - 8,
        "platforms": platforms,
        "enemies": enemies,
        "items": items,
        "npcs": npcs,
        "fires": [],
        "player_start": (30, PLAY_H - 40),
        "exit_x": 475,
        "goal_count": 2,
        "border_color": None,
        "draw_bg": draw_house_bg,
    }


def draw_house_bg(surf, cam_x, level):
    """Draw house background."""
    surf.fill(C_LAVENDER)
    # Wall panels
    pygame.draw.rect(surf, C_LPURPLE, (0 - cam_x, 0, 512, PLAY_H - 8))
    # Wall accent line at top
    pygame.draw.rect(surf, C_LAVENDER, (0 - cam_x, 0, 512, 3))
    # Room divider
    pygame.draw.rect(surf, C_WHITE, (250 - cam_x, 0, 3, PLAY_H - 8))
    # Floor
    pygame.draw.rect(surf, C_PINK, (0 - cam_x, PLAY_H - 8, 512, 16))
    # Door (left side - entry)
    draw_door(surf, 15, PLAY_H - 48, cam_x, C_BLUE)
    # Bookshelves
    draw_bookshelf(surf, 140, PLAY_H - 80, cam_x)
    draw_bookshelf(surf, 275, PLAY_H - 80, cam_x)
    # Couch
    draw_couch(surf, 380, PLAY_H - 32, cam_x)
    # Small table with fishbowl
    draw_table(surf, 90, PLAY_H - 30, cam_x)
    # Fishbowl on table
    fx = 95 - cam_x
    fy = PLAY_H - 40
    pygame.draw.ellipse(surf, C_CYAN, (fx, fy, 10, 10))
    pygame.draw.ellipse(surf, C_LBLUE, (fx + 1, fy + 1, 8, 8))
    # Picture on wall (left room)
    pygame.draw.rect(surf, C_BROWN, (60 - cam_x, 30, 24, 20))
    pygame.draw.rect(surf, C_LBLUE, (62 - cam_x, 32, 20, 16))
    # Picture on wall (right room)
    pygame.draw.rect(surf, C_BROWN, (330 - cam_x, 30, 28, 22))
    pygame.draw.rect(surf, C_DRED, (332 - cam_x, 32, 24, 18))
    # Shelves on wall
    pygame.draw.rect(surf, C_ORANGE, (180 - cam_x, 50, 40, 4))
    pygame.draw.rect(surf, C_ORANGE, (320 - cam_x, 45, 35, 4))
    # Plant/cactus between bookshelves
    px = 260 - cam_x
    pygame.draw.rect(surf, C_BROWN, (px + 2, PLAY_H - 22, 6, 14))
    pygame.draw.rect(surf, C_GREEN, (px, PLAY_H - 30, 10, 12))
    pygame.draw.rect(surf, C_DGREEN, (px + 3, PLAY_H - 36, 4, 8))
    # Exit door (right side - to kitchen)
    draw_door(surf, 470, PLAY_H - 48, cam_x, C_DGREEN)
    # Arrow hint near exit
    pygame.draw.rect(surf, C_FIRE_Y, (460 - cam_x, PLAY_H - 55, 6, 3))


def create_level_school():
    """Level 2: School Hallway."""
    platforms = [
        Platform(0, PLAY_H - 8, 768, 16, C_DRED),  # floor
        # Locker tops as platforms
        Platform(150, PLAY_H - 56, 72, 6, C_GRAY),
        Platform(350, PLAY_H - 56, 72, 6, C_GRAY),
        Platform(550, PLAY_H - 56, 72, 6, C_GRAY),
        # Higher walkway
        Platform(250, PLAY_H - 90, 60, 6, C_GRAY),
        Platform(480, PLAY_H - 80, 50, 6, C_GRAY),
    ]
    enemies = [
        Enemy(200, 80, "spider", 100, 500),
        Enemy(500, 60, "spider", 400, 700),
    ]
    items = [
        Collectible(270, PLAY_H - 106, "spray_can", "SPRAY CAN"),
        Collectible(680, PLAY_H - 24, "key", "HALL PASS"),
    ]
    npcs = [
        NPC(350, PLAY_H - 36, "student", 300, 450),
        NPC(650, PLAY_H - 34, "lunch_lady"),
    ]
    return {
        "width": 768,
        "bg_color": C_SKYBLUE,
        "floor_y": PLAY_H - 8,
        "platforms": platforms,
        "enemies": enemies,
        "items": items,
        "npcs": npcs,
        "fires": [],
        "player_start": (30, PLAY_H - 40),
        "exit_x": 730,
        "goal_count": 2,
        "border_color": C_FIRE_Y,
        "draw_bg": draw_school_bg,
    }


def draw_school_bg(surf, cam_x, level):
    """Draw school hallway background."""
    # Sky blue walls
    surf.fill(C_SKYBLUE)
    # Ceiling with diagonal hatching
    pygame.draw.rect(surf, C_GRAY, (0 - cam_x, 0, 768, 20))
    for i in range(-20, 768 + 20, 8):
        x = i - int(cam_x) % 8
        pygame.draw.line(surf, C_DGRAY, (x, 0), (x + 20, 20), 1)
    # Floor
    pygame.draw.rect(surf, C_DRED, (0 - cam_x, PLAY_H - 8, 768, 16))
    # Baseboard
    pygame.draw.rect(surf, C_BROWN, (0 - cam_x, PLAY_H - 10, 768, 2))
    # Lockers along the back
    for lx in range(50, 700, 100):
        draw_lockers(surf, lx, PLAY_H - 64, cam_x, 6)
    # Clocks
    draw_clock(surf, 120, 24, cam_x)
    draw_clock(surf, 500, 24, cam_x)
    # Water fountain
    draw_water_fountain(surf, 320, PLAY_H - 32, cam_x)
    # Doors
    draw_door(surf, 10, PLAY_H - 48, cam_x, C_PURPLE)
    draw_door(surf, 400, PLAY_H - 48, cam_x, C_PURPLE)
    draw_door(surf, 730, PLAY_H - 48, cam_x, C_PURPLE)
    # Bulletin board
    bx = 280 - cam_x
    pygame.draw.rect(surf, C_BROWN, (bx, 28, 30, 24))
    pygame.draw.rect(surf, C_CREAM, (bx + 2, 30, 12, 10))
    pygame.draw.rect(surf, C_WHITE, (bx + 16, 30, 12, 10))
    pygame.draw.rect(surf, C_CREAM, (bx + 5, 42, 8, 8))
    # Second bulletin board
    bx2 = 600 - cam_x
    pygame.draw.rect(surf, C_BROWN, (bx2, 28, 26, 20))
    pygame.draw.rect(surf, C_WHITE, (bx2 + 2, 30, 22, 16))


def create_level_street():
    """Level 3: Street to Krusty Burger."""
    platforms = [
        Platform(0, PLAY_H - 8, 1024, 16, C_GRAY),  # sidewalk
        # Stepping platforms under Krusty Burger (x~440)
        Platform(420, PLAY_H - 50, 40, 6, C_DGRAY),   # dumpster
        Platform(425, PLAY_H - 75, 30, 5, C_ORANGE),  # awning
        # Stepping platforms under Spray Can (x~880)
        Platform(860, PLAY_H - 50, 40, 6, C_DGRAY),   # dumpster
        Platform(865, PLAY_H - 75, 30, 5, C_ORANGE),  # awning
        # Additional scenery platforms
        Platform(150, PLAY_H - 50, 30, 6, C_DGRAY),   # dumpster
        Platform(600, PLAY_H - 50, 30, 6, C_DGRAY),   # box
        # Near exit
        Platform(940, PLAY_H - 50, 50, 6, C_ORANGE),
    ]
    enemies = [
        Enemy(300, PLAY_H - 20, "spider", 200, 500),
        Enemy(600, PLAY_H - 20, "spider", 500, 800),
    ]
    items = [
        Collectible(435, PLAY_H - 91, "hamburger", "KRUSTY BURGER"),
        Collectible(875, PLAY_H - 91, "spray_can", "SPRAY CAN"),
    ]
    npcs = [
        NPC(200, PLAY_H - 36, "student", 150, 350),
    ]
    return {
        "width": 1024,
        "bg_color": C_SKYBLUE,
        "floor_y": PLAY_H - 8,
        "platforms": platforms,
        "enemies": enemies,
        "items": items,
        "npcs": npcs,
        "fires": [],
        "player_start": (30, PLAY_H - 40),
        "exit_x": 990,
        "goal_count": 1,
        "border_color": None,
        "draw_bg": draw_street_bg,
    }


def draw_street_bg(surf, cam_x, level):
    """Draw street background."""
    # Sky
    surf.fill(C_SKYBLUE)
    # Grass
    pygame.draw.rect(surf, C_GREEN, (0 - cam_x, PLAY_H - 50, 1024, 42))
    # Sidewalk
    pygame.draw.rect(surf, C_GRAY, (0 - cam_x, PLAY_H - 8, 1024, 16))
    pygame.draw.rect(surf, C_LGRAY, (0 - cam_x, PLAY_H - 10, 1024, 3))
    # Crack lines in sidewalk
    for i in range(0, 1024, 32):
        x = i - cam_x
        pygame.draw.line(surf, C_DGRAY, (x, PLAY_H - 8), (x, PLAY_H + 8), 1)

    # Buildings on left
    # Building 1 - red/brick
    bx = 0 - cam_x
    pygame.draw.rect(surf, C_RED, (bx, 0, 120, PLAY_H - 50))
    pygame.draw.rect(surf, C_TEAL, (bx, PLAY_H - 100, 120, 50))
    # Windows
    for wy in range(20, 80, 30):
        for wx in range(20, 100, 40):
            pygame.draw.rect(surf, C_SKYBLUE, (bx + wx, wy, 16, 20))

    # Krusty Burger building (right side)
    kx = 780 - cam_x
    pygame.draw.rect(surf, C_ORANGE, (kx, 0, 244, PLAY_H - 50))
    pygame.draw.rect(surf, C_DRED, (kx, 0, 244, 20))
    # Sign
    pygame.draw.rect(surf, C_FIRE_Y, (kx + 20, 30, 80, 30))
    # Window
    pygame.draw.rect(surf, C_SKYBLUE, (kx + 40, 70, 50, 40))

    # Power line poles
    for px in [120, 380, 640]:
        pole_x = px - cam_x
        pygame.draw.rect(surf, C_BROWN, (pole_x, 20, 4, PLAY_H - 70))
    # Power lines
    for px_start, px_end in [(120, 320), (380, 580), (640, 840)]:
        sx = px_start - cam_x + 2
        ex = px_end - cam_x + 2
        pygame.draw.line(surf, C_DGRAY, (sx, 50), (ex, 50), 1)

    # Bushes
    for bx_pos in [150, 350, 550]:
        bx2 = bx_pos - cam_x
        pygame.draw.ellipse(surf, C_DGREEN, (bx2, PLAY_H - 60, 30, 15))

    # Grass tufts
    for gx in range(0, 1024, 40):
        x = gx - cam_x
        pygame.draw.rect(surf, C_DGREEN, (x, PLAY_H - 52, 2, 4))
        pygame.draw.rect(surf, C_DGREEN, (x + 8, PLAY_H - 54, 2, 6))


def create_level_thought():
    """Level 4: Thought Bubble - surreal conversation level."""
    platforms = [
        # Floating platforms inside thought bubble
        Platform(40, PLAY_H - 30, 180, 8, C_WHITE),   # bottom floor
        Platform(30, PLAY_H - 70, 70, 6, C_WHITE),    # left mid
        Platform(140, PLAY_H - 65, 60, 6, C_WHITE),   # right mid
        Platform(80, PLAY_H - 105, 60, 6, C_WHITE),   # center high
        Platform(30, PLAY_H - 140, 50, 6, C_WHITE),   # left top
        Platform(150, PLAY_H - 130, 50, 6, C_WHITE),  # right top
    ]
    enemies = []
    items = [
        Collectible(90, PLAY_H - 120, "hamburger", "'STEAMED HAMS'"),
        Collectible(40, PLAY_H - 156, "key", "UPSTATE NEW YORK"),
    ]
    npcs = [
        NPC(160, PLAY_H - 58, "chalmers"),
    ]
    return {
        "width": NES_W,
        "bg_color": C_BLACK,
        "floor_y": PLAY_H - 30,
        "platforms": platforms,
        "enemies": enemies,
        "items": items,
        "npcs": npcs,
        "fires": [],
        "player_start": (100, PLAY_H - 60),
        "exit_x": -1,  # no exit, complete when all items collected
        "goal_count": 2,
        "border_color": None,
        "draw_bg": draw_thought_bg,
    }


def draw_thought_bg(surf, cam_x, level):
    """Draw thought bubble background."""
    surf.fill(C_BLACK)
    # Thought bubble outline
    points = []
    cx, cy = NES_W // 2, (PLAY_H) // 2 - 10
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        # Lumpy cloud shape
        r = 90 + 15 * math.sin(rad * 6) + 10 * math.cos(rad * 3)
        rx = r * 1.2
        ry = r * 0.7
        px = cx + int(rx * math.cos(rad))
        py = cy + int(ry * math.sin(rad))
        points.append((px, py))
    if len(points) > 2:
        pygame.draw.polygon(surf, C_BLACK, points)
        pygame.draw.polygon(surf, C_WHITE, points, 2)
    # Small bubble circles at bottom right
    pygame.draw.circle(surf, C_WHITE, (NES_W - 40, PLAY_H - 10), 8, 1)
    pygame.draw.circle(surf, C_WHITE, (NES_W - 25, PLAY_H + 5), 5, 1)
    # Divider line
    pygame.draw.rect(surf, C_WHITE, (0, PLAY_H - 2, NES_W, 2))


def create_level_house_fire():
    """Level 5: Skinner's House on Fire."""
    platforms = [
        Platform(0, PLAY_H - 8, 512, 16, C_PINK),       # floor
        Platform(65, PLAY_H - 36, 24, 6, C_BROWN),       # table
        Platform(90, PLAY_H - 62, 56, 6, C_ORANGE),      # shelf
        Platform(210, PLAY_H - 80, 56, 6, C_ORANGE),     # higher shelf
        Platform(280, PLAY_H - 72, 30, 4, C_BROWN, visible=False),  # bookshelf top
        Platform(378, PLAY_H - 32, 6, 24, C_DGREEN),     # couch arm
    ]
    enemies = [
        Enemy(200, 60, "spider", 100, 350),
    ]
    items = [
        Collectible(225, PLAY_H - 96, "wine", "WINE"),
    ]
    npcs = [
        NPC(430, PLAY_H - 36, "chalmers"),
    ]
    fires = [
        FireHazard(120, PLAY_H - 24),
        FireHazard(180, PLAY_H - 24),
        FireHazard(260, PLAY_H - 24),
        FireHazard(330, PLAY_H - 24),
        FireHazard(385, PLAY_H - 44),  # on couch
        FireHazard(405, PLAY_H - 44),
    ]
    return {
        "width": 512,
        "bg_color": C_LAVENDER,
        "floor_y": PLAY_H - 8,
        "platforms": platforms,
        "enemies": enemies,
        "items": items,
        "npcs": npcs,
        "fires": fires,
        "player_start": (30, PLAY_H - 40),
        "exit_x": 475,
        "goal_count": 1,
        "border_color": None,
        "draw_bg": draw_house_fire_bg,
    }


def draw_house_fire_bg(surf, cam_x, level):
    """Draw house on fire background."""
    draw_house_bg(surf, cam_x, level)
    # Orange glow overlay on right side
    glow = pygame.Surface((512, PLAY_H), pygame.SRCALPHA)
    glow.fill((248, 120, 0, 30))
    surf.blit(glow, (0 - cam_x, 0))


# ============================================================
# CUTSCENE SYSTEM
# ============================================================
CUTSCENES = [
    # Cutscene 0: Chalmers arrives
    {
        "scenes": [
            {
                "draw": "arrival",
                "lines": [
                    "WELL, SEYMOUR, I MADE IT,\nDESPITE YOUR DIRECTIONS.",
                    "AH, SUPERINTENDENT\nCHALMERS! WELCOME!\nI HOPE YOU'RE PREPARED FOR\nAN UNFORGETTABLE LUNCHEON!",
                    "YEAH.",
                ],
            },
        ],
    },
    # Cutscene 1: Oven on fire / Idea
    {
        "scenes": [
            {
                "draw": "fire_shock",
                "lines": [
                    "OH EGADS! MY ROAST\nIS RUINED!",
                ],
            },
            {
                "draw": "idea",
                "lines": [
                    "BUT WHAT IF I WERE\nTO PURCHASE FAST FOOD\nAND DISGUISE IT\nAS MY OWN COOKING?",
                    "OH HO HO HO HO!\nDELIGHTFULLY DEVILISH,\nSEYMOUR!",
                ],
            },
        ],
    },
    # Cutscene 2: Window escape
    {
        "scenes": [
            {
                "draw": "window_escape",
                "lines": [
                    "SEYMOUR!",
                    "SUPERINTENDENT!\nI WAS JUST, UH...\nSTRETCHING MY CALVES\nON THE WINDOWSILL.",
                    "WHY IS THERE SMOKE COMING\nOUT OF YOUR OVEN, SEYMOUR?",
                ],
            },
            {
                "draw": "steam_excuse",
                "lines": [
                    "UH... OOH!\nTHAT ISN'T SMOKE.\nIT'S STEAM! STEAM FROM\nTHE STEAMED CLAMS\nWE'RE HAVING.",
                    "MMHM.",
                ],
            },
        ],
    },
    # Cutscene 3: Serving hamburgers
    {
        "scenes": [
            {
                "draw": "serving",
                "lines": [
                    "SUPERINTENDENT, I HOPE\nYOU'RE READY FOR\nMOUTH-WATERING\nHAMBURGERS!",
                    "I THOUGHT WE WERE HAVING\nSTEAMED CLAMS.",
                    "OH NO, I SAID\nSTEAMED HAMS!\nTHAT'S WHAT I CALL\nHAMBURGERS.",
                ],
            },
        ],
    },
    # Cutscene 4: Dinner dialogue
    {
        "scenes": [
            {
                "draw": "dinner",
                "lines": [
                    "YOU CALL HAMBURGERS\nSTEAMED HAMS?",
                    "YES! IT'S A REGIONAL\nDIALECT.",
                    "UH HUH. WHAT REGION?",
                    "UH... UPSTATE NEW YORK.",
                    "REALLY? WELL I'M FROM\nUTICA AND I'VE NEVER\nHEARD ANYONE USE THE\nPHRASE STEAMED HAMS.",
                    "OH, NOT IN UTICA, NO.\nIT'S AN ALBANY\nEXPRESSION.",
                ],
            },
            {
                "draw": "dinner_eating",
                "lines": [
                    "YOU KNOW, THESE HAMBURGERS\nARE QUITE SIMILAR TO THE\nONES THEY HAVE AT\nKRUSTY BURGER.",
                    "OH HO HO HO, NO!\nPATENTED SKINNER BURGERS.\nOLD FAMILY RECIPE.",
                    "FOR STEAMED HAMS.",
                    "YES.",
                    "AND YOU CALL THEM\nSTEAMED HAMS DESPITE\nTHE FACT THAT THEY\nARE OBVIOUSLY GRILLED.",
                ],
            },
        ],
    },
    # Cutscene 5: Aurora Borealis
    {
        "scenes": [
            {
                "draw": "aurora",
                "lines": [
                    "YES. I SHOULD BE--\nGOOD LORD,\nWHAT IS HAPPENING\nIN THERE!?",
                    "AURORA BOREALIS.",
                    "A-AURORA BOREALIS!?\nAT THIS TIME OF YEAR,\nAT THIS TIME OF DAY,\nIN THIS PART OF THE\nCOUNTRY, LOCALIZED\nENTIRELY WITHIN YOUR\nKITCHEN!?",
                    "YES.",
                    "MAY I SEE IT?",
                    "...NO.",
                ],
            },
        ],
    },
    # Cutscene 6: Ending
    {
        "scenes": [
            {
                "draw": "mother",
                "lines": [
                    "SEYMOUR! THE HOUSE\nIS ON FIRE!",
                    "NO, MOTHER.\nIT'S JUST THE\nNORTHERN LIGHTS.",
                ],
            },
            {
                "draw": "goodbye",
                "lines": [
                    "WELL, SEYMOUR, YOU ARE\nAN ODD FELLOW, BUT I\nMUST SAY...\nYOU STEAM A GOOD HAM.",
                ],
            },
            {
                "draw": "fire_ending",
                "lines": [
                    "HELP! HEEELP!",
                ],
            },
        ],
    },
]


def draw_cutscene_illustration(surf, scene_name, frame=0):
    """Draw a cutscene illustration on the NES surface."""
    # All cutscene illustrations are drawn in a centered box
    box_x, box_y = 48, 16
    box_w, box_h = 160, 120

    if scene_name == "arrival":
        # Chalmers and Skinner at the front door
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Door frame
        pygame.draw.rect(surf, C_LAVENDER, (box_x + box_w // 2 - 2, box_y, 4, box_h))
        # Chalmers (left side)
        s = create_chalmers_sprite(True, frame // 10)
        surf.blit(pygame.transform.scale(s, (32, 56)),
                  (box_x + 15, box_y + 30))
        # Skinner (right side, in apron)
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (32, 56)),
                  (box_x + box_w // 2 + 15, box_y + 30))
        # Apron overlay
        pygame.draw.rect(surf, C_WHITE,
                         (box_x + box_w // 2 + 20, box_y + 52, 22, 28))
        # Picture on wall
        pygame.draw.rect(surf, C_DGRAY, (box_x + box_w - 30, box_y + 10, 20, 16))
        pygame.draw.rect(surf, C_PURPLE, (box_x + box_w - 28, box_y + 12, 16, 12))

    elif scene_name == "fire_shock":
        # Skinner sees fire in oven
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        # TV frame style border
        pygame.draw.rect(surf, C_DGRAY, (box_x - 4, box_y - 4, box_w + 8, box_h + 8))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        # Skinner (shocked)
        s = create_skinner_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (40, 70)),
                  (box_x + 50, box_y + 10))
        # Flames
        for i in range(5):
            fx = box_x + 30 + i * 15
            fy = box_y + 60 + random.randint(-5, 0)
            c = [C_FIRE_Y, C_FIRE_O, C_FIRE_R][i % 3]
            pygame.draw.rect(surf, c, (fx, fy, 10, 20 + random.randint(0, 10)))
            pygame.draw.rect(surf, C_FIRE_Y, (fx + 2, fy - 5, 6, 10))

    elif scene_name == "idea":
        # Skinner in kitchen, window showing Krusty Burger
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Oven (left) with smoke
        pygame.draw.rect(surf, C_LGRAY, (box_x + 5, box_y + 60, 30, 50))
        pygame.draw.rect(surf, C_DGRAY, (box_x + 7, box_y + 65, 26, 20))
        # Smoke
        for i in range(3):
            sy = box_y + 20 + i * 15 + (frame // 5 % 3)
            sx = box_x + 15 + (frame // 8 % 5)
            pygame.draw.rect(surf, C_LGRAY, (sx, sy, 8, 12))
        # Skinner
        s = create_skinner_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (32, 56)),
                  (box_x + 55, box_y + 30))
        # Window with Krusty Burger
        wx = box_x + 100
        wy = box_y + 15
        pygame.draw.rect(surf, C_BLUE, (wx, wy, 50, 50))
        pygame.draw.rect(surf, C_BROWN, (wx, wy, 50, 50), 2)
        # Krusty Burger sign (small)
        pygame.draw.rect(surf, C_GREEN, (wx + 5, wy + 30, 40, 15))
        pygame.draw.rect(surf, C_ORANGE, (wx + 10, wy + 20, 25, 12))
        # Burger on sign
        draw_hamburger(surf, wx + 18, wy + 5, 8)

    elif scene_name in ("window_escape", "steam_excuse"):
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Oven with smoke
        pygame.draw.rect(surf, C_LGRAY, (box_x + 5, box_y + 60, 30, 50))
        # Smoke
        for i in range(4):
            sy = box_y + 10 + i * 12
            sx = box_x + 12 + (i * 3) % 5
            pygame.draw.rect(surf, C_LGRAY, (sx, sy, 10, 15))
        # Chalmers (left, suspicious)
        s = create_chalmers_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (32, 56)),
                  (box_x + 20, box_y + 25))
        # Skinner (right, nervous)
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (32, 56)),
                  (box_x + 95, box_y + 25))
        # Window with Krusty Burger
        wx = box_x + 105
        wy = box_y + 10
        pygame.draw.rect(surf, C_BLUE, (wx, wy, 40, 35))
        pygame.draw.rect(surf, C_BROWN, (wx, wy, 40, 35), 2)

    elif scene_name == "serving":
        # Skinner presents hamburgers at table
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Table
        pygame.draw.rect(surf, C_WHITE, (box_x + 20, box_y + 75, 120, 5))
        pygame.draw.rect(surf, C_LGRAY, (box_x + 30, box_y + 80, 4, 30))
        pygame.draw.rect(surf, C_LGRAY, (box_x + 126, box_y + 80, 4, 30))
        # Chalmers seated (left)
        s = create_chalmers_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (32, 56)),
                  (box_x + 15, box_y + 20))
        # Skinner with tray (right)
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (32, 56)),
                  (box_x + 100, box_y + 15))
        # Tray of hamburgers
        pygame.draw.rect(surf, C_DGRAY, (box_x + 65, box_y + 35, 50, 4))
        for hx in range(4):
            draw_hamburger(surf, box_x + 68 + hx * 12, box_y + 25, 8)

    elif scene_name in ("dinner", "dinner_eating"):
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Dining table
        pygame.draw.rect(surf, C_WHITE, (box_x + 20, box_y + 75, 120, 5))
        # Chairs
        pygame.draw.rect(surf, C_DRED, (box_x + 10, box_y + 45, 6, 40))
        pygame.draw.rect(surf, C_DRED, (box_x + 144, box_y + 45, 6, 40))
        # Chalmers (left, eating)
        s = create_chalmers_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (28, 50)),
                  (box_x + 18, box_y + 25))
        # Skinner (right)
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (28, 50)),
                  (box_x + 108, box_y + 25))
        # Wine bucket
        pygame.draw.rect(surf, C_LGRAY, (box_x + 70, box_y + 60, 16, 18))
        pygame.draw.rect(surf, C_WHITE, (box_x + 73, box_y + 58, 2, 8))
        # Hamburger on plate
        draw_hamburger(surf, box_x + 72, box_y + 68, 10)
        # Glasses
        pygame.draw.rect(surf, C_LGRAY, (box_x + 50, box_y + 68, 4, 8))
        pygame.draw.rect(surf, C_LGRAY, (box_x + 100, box_y + 68, 4, 8))
        # Smoke if dinner_eating
        if scene_name == "dinner_eating":
            for i in range(2):
                sx = box_x + 140 + (frame // 6 % 3)
                sy = box_y + 10 + i * 15
                pygame.draw.rect(surf, C_LGRAY, (sx, sy, 6, 10))

    elif scene_name == "aurora":
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Window with fire glow
        wx = box_x + 5
        wy = box_y + 10
        pygame.draw.rect(surf, C_LAVENDER, (wx, wy, 40, 40))
        pygame.draw.rect(surf, C_WHITE, (wx, wy, 40, 40), 2)
        # Cross bars on window
        pygame.draw.rect(surf, C_WHITE, (wx + 19, wy, 2, 40))
        pygame.draw.rect(surf, C_WHITE, (wx, wy + 19, 40, 2))
        # Flames in window
        for i in range(3):
            fc = [C_FIRE_Y, C_FIRE_O, C_FIRE_R][i]
            fy_off = (frame // 4 + i * 3) % 6
            pygame.draw.rect(surf, fc, (wx + 4 + i * 12, wy + 22 - fy_off, 8, 18))
        # Chalmers (center-left)
        s = create_chalmers_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (28, 50)),
                  (box_x + 50, box_y + 35))
        # Skinner (center-right)
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (28, 50)),
                  (box_x + 100, box_y + 35))

    elif scene_name == "mother":
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Window with fire
        wx = box_x + 5
        wy = box_y + 10
        pygame.draw.rect(surf, C_LAVENDER, (wx, wy, 40, 40))
        pygame.draw.rect(surf, C_WHITE, (wx, wy, 40, 40), 2)
        pygame.draw.rect(surf, C_WHITE, (wx + 19, wy, 2, 40))
        pygame.draw.rect(surf, C_WHITE, (wx, wy + 19, 40, 2))
        for i in range(3):
            fc = [C_FIRE_Y, C_FIRE_O, C_FIRE_R][i]
            fy_off = (frame // 4 + i * 3) % 6
            pygame.draw.rect(surf, fc, (wx + 4 + i * 12, wy + 22 - fy_off, 8, 18))
        # Chalmers
        s = create_chalmers_sprite(True, 0)
        surf.blit(pygame.transform.scale(s, (28, 50)),
                  (box_x + 50, box_y + 35))
        # Skinner
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (28, 50)),
                  (box_x + 100, box_y + 35))

    elif scene_name == "goodbye":
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Porch/doorway
        pygame.draw.rect(surf, C_LAVENDER, (box_x + box_w // 2, box_y, box_w // 2, box_h))
        # Chalmers leaving
        s = create_chalmers_sprite(False, frame // 10)
        surf.blit(pygame.transform.scale(s, (28, 50)),
                  (box_x + 30, box_y + 40))
        # Skinner in doorway
        s2 = create_skinner_sprite(False, 0)
        surf.blit(pygame.transform.scale(s2, (28, 50)),
                  (box_x + 100, box_y + 40))

    elif scene_name == "fire_ending":
        pygame.draw.rect(surf, C_BLACK, (0, 0, NES_W, NES_H))
        # House exterior with fire
        # Sky
        pygame.draw.rect(surf, C_LPURPLE, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
        # Window with fire
        pygame.draw.rect(surf, C_LAVENDER, (box_x, box_y, box_w, box_h))
        # Window
        wx = box_x + 10
        wy = box_y + 15
        pygame.draw.rect(surf, C_WHITE, (wx, wy, 60, 50), 2)
        pygame.draw.rect(surf, C_WHITE, (wx + 29, wy, 2, 50))
        pygame.draw.rect(surf, C_WHITE, (wx, wy + 24, 60, 2))
        # Curtains
        pygame.draw.rect(surf, C_PINK, (wx + 60, wy, 10, 50))
        # Flames
        for i in range(4):
            fc = [C_FIRE_Y, C_FIRE_O, C_FIRE_R, C_FIRE_O][i]
            fy_off = (frame // 3 + i * 4) % 8
            pygame.draw.rect(surf, fc, (wx + 5 + i * 14, wy + 25 - fy_off, 10, 25))
        # Door
        pygame.draw.rect(surf, C_LAVENDER, (box_x + 100, wy, 40, 65))
        pygame.draw.rect(surf, C_DGRAY, (box_x + 100, wy, 40, 65), 2)


# ============================================================
# HUD
# ============================================================
def draw_hud(surf, player, font):
    """Draw the game HUD at the bottom of the screen."""
    hud_y = PLAY_H
    # Background
    pygame.draw.rect(surf, C_BLACK, (0, hud_y, NES_W, HUD_H))

    # Item name box
    pygame.draw.rect(surf, C_BLUE, (4, hud_y + 2, 100, 12), 1)
    name = player.current_item_name or ""
    text = font.render(name, False, C_WHITE)
    surf.blit(text, (6, hud_y + 3))

    # Life icons
    label = font.render("LIFE", False, C_WHITE)
    surf.blit(label, (6, hud_y + 30))
    for i in range(player.health):
        draw_graduation_cap(surf, 6 + i * 12, hud_y + 18)

    # Score box
    pygame.draw.rect(surf, C_BLUE, (80, hud_y + 18, 50, 18), 1)
    score_text = font.render(str(player.score), False, C_WHITE)
    surf.blit(score_text, (84, hud_y + 20))
    score_label = font.render("SCORE", False, C_WHITE)
    surf.blit(score_label, (82, hud_y + 30))

    # Lives box
    pygame.draw.rect(surf, C_BLUE, (136, hud_y + 18, 24, 18), 1)
    lives_text = font.render(str(player.lives), False, C_WHITE)
    surf.blit(lives_text, (144, hud_y + 20))
    lives_label = font.render("LIVES", False, C_WHITE)
    surf.blit(lives_label, (134, hud_y + 30))

    # Goals box
    pygame.draw.rect(surf, C_BLUE, (166, hud_y + 18, 24, 18), 1)
    goals_text = font.render(str(player.goals_done), False, C_WHITE)
    surf.blit(goals_text, (174, hud_y + 20))
    goals_label = font.render("GOALS", False, C_WHITE)
    surf.blit(goals_label, (163, hud_y + 30))

    # Item icon box
    pygame.draw.rect(surf, C_BLUE, (196, hud_y + 16, 22, 22), 1)
    if player.current_item_icon:
        player.current_item_icon(surf, 200, hud_y + 18)

    # Border
    pygame.draw.rect(surf, C_BLUE, (0, hud_y, NES_W, HUD_H), 1)


# ============================================================
# TITLE SCREEN
# ============================================================
def draw_title_screen(surf, font, frame):
    """Draw the NES title screen."""
    surf.fill(C_BLACK)

    # Skinner's house (simplified)
    # Sky
    pygame.draw.rect(surf, C_SKYBLUE, (0, 0, NES_W, 120))
    # Clouds
    for cx_pos, cy_pos in [(40, 20), (140, 30), (200, 15)]:
        pygame.draw.ellipse(surf, C_WHITE, (cx_pos, cy_pos, 40, 16))
    # Trees
    pygame.draw.rect(surf, C_DGREEN, (0, 40, 30, 80))
    pygame.draw.rect(surf, C_GREEN, (5, 30, 25, 50))
    pygame.draw.rect(surf, C_DGREEN, (220, 50, 36, 70))
    pygame.draw.rect(surf, C_GREEN, (225, 35, 30, 60))
    # House
    # Roof
    points = [(70, 40), (128, 10), (186, 40)]
    pygame.draw.polygon(surf, C_BLUE, points)
    # Walls
    pygame.draw.rect(surf, C_LPURPLE, (70, 40, 116, 80))
    # Windows
    pygame.draw.rect(surf, C_LAVENDER, (80, 50, 20, 20))
    pygame.draw.rect(surf, C_LAVENDER, (150, 50, 20, 20))
    # Shutters
    pygame.draw.rect(surf, C_FIRE_Y, (76, 50, 4, 20))
    pygame.draw.rect(surf, C_FIRE_Y, (100, 50, 4, 20))
    pygame.draw.rect(surf, C_FIRE_Y, (146, 50, 4, 20))
    pygame.draw.rect(surf, C_FIRE_Y, (170, 50, 4, 20))
    # Door
    pygame.draw.rect(surf, C_BLUE, (113, 80, 18, 40))
    pygame.draw.rect(surf, C_DGRAY, (115, 82, 14, 36))
    # Porch
    pygame.draw.rect(surf, C_BLUE, (60, 78, 136, 4))
    # Steps
    pygame.draw.rect(surf, C_LGRAY, (105, 120, 34, 6))
    # Driveway
    pygame.draw.rect(surf, C_LGRAY, (40, 120, 70, 30))
    # Grass
    pygame.draw.rect(surf, C_GREEN, (0, 120, NES_W, 30))
    # Circular window
    pygame.draw.circle(surf, C_LPURPLE, (128, 28), 8)
    pygame.draw.circle(surf, C_WHITE, (128, 28), 8, 1)
    pygame.draw.line(surf, C_WHITE, (120, 28), (136, 28), 1)
    pygame.draw.line(surf, C_WHITE, (128, 20), (128, 36), 1)

    # Skinner on porch
    s = create_skinner_sprite(True, (frame // 15) % 2)
    surf.blit(pygame.transform.scale(s, (16, 28)), (120, 90))

    # Title text
    title1 = font.render("STEAMED HAMS", False, C_WHITE)
    title2 = font.render("THE GAME", False, C_WHITE)
    tw1 = title1.get_width()
    tw2 = title2.get_width()
    surf.blit(title1, (NES_W // 2 - tw1 // 2, 160))
    surf.blit(title2, (NES_W // 2 - tw2 // 2, 175))

    # Blink "PRESS START"
    if (frame // 30) % 2 == 0:
        start_text = font.render("PRESS ENTER TO START", False, C_WHITE)
        sw = start_text.get_width()
        surf.blit(start_text, (NES_W // 2 - sw // 2, 200))

    # Copyright
    copy_text = font.render("(C) 1991 IMAGINEERING INC.", False, C_DGRAY)
    cw = copy_text.get_width()
    surf.blit(copy_text, (NES_W // 2 - cw // 2, 225))


# ============================================================
# CREDITS SCREEN
# ============================================================
def draw_credits(surf, font, player, frame):
    """Draw the credits/ending screen."""
    surf.fill(C_BLACK)

    # Score display
    score_label = font.render("1UP       HI-SCORE", False, C_WHITE)
    surf.blit(score_label, (30, 8))
    score_val = font.render(f"{player.score}      99650", False, C_WHITE)
    surf.blit(score_val, (30, 18))

    # Fire truck
    box_x, box_y = 48, 30
    box_w, box_h = 160, 100
    pygame.draw.rect(surf, C_SKYBLUE, (box_x, box_y, box_w, box_h))
    pygame.draw.rect(surf, C_WHITE, (box_x, box_y, box_w, box_h), 1)
    # Road
    pygame.draw.rect(surf, C_GRAY, (box_x, box_y + 80, box_w, 20))
    # Fire truck body
    tx = box_x + 20
    ty = box_y + 30
    pygame.draw.rect(surf, C_DRED, (tx, ty, 120, 50))
    # Cab
    pygame.draw.rect(surf, C_DRED, (tx, ty, 50, 50))
    pygame.draw.rect(surf, C_LAVENDER, (tx + 5, ty + 5, 20, 20))
    pygame.draw.rect(surf, C_LAVENDER, (tx + 30, ty + 5, 15, 20))
    # Ladder
    pygame.draw.rect(surf, C_DGRAY, (tx + 55, ty + 5, 60, 8))
    pygame.draw.rect(surf, C_LGRAY, (tx + 55, ty + 5, 60, 3))
    # Wheels
    pygame.draw.circle(surf, C_DGRAY, (tx + 25, ty + 52), 10)
    pygame.draw.circle(surf, C_GRAY, (tx + 25, ty + 52), 5)
    pygame.draw.circle(surf, C_DGRAY, (tx + 100, ty + 52), 10)
    pygame.draw.circle(surf, C_GRAY, (tx + 100, ty + 52), 5)
    # Lights
    if frame % 20 < 10:
        pygame.draw.rect(surf, C_LRED, (tx + 15, ty - 5, 8, 6))
    else:
        pygame.draw.rect(surf, C_LBLUE, (tx + 15, ty - 5, 8, 6))
    # Grille
    pygame.draw.rect(surf, C_GRAY, (tx + 110, ty + 30, 10, 16))
    pygame.draw.rect(surf, C_LGRAY, (tx + 112, ty + 32, 6, 4))
    pygame.draw.rect(surf, C_LGRAY, (tx + 112, ty + 40, 6, 4))

    # Credits text
    credits = [
        "STORY BY",
        "BILL OAKLEY",
        "",
        "PROGRAMMED BY",
        "JIM REARDON",
        "",
        "GAME DEVELOPED BY",
        "IMAGINEERING INC.",
        "",
        "COPYRIGHT 1991",
    ]
    y = 140
    for line in credits:
        if line:
            t = font.render(line, False, C_WHITE)
            tw = t.get_width()
            surf.blit(t, (NES_W // 2 - tw // 2, y))
        y += 10

    if (frame // 30) % 2 == 0:
        end_t = font.render("PRESS ENTER", False, C_LGRAY)
        surf.blit(end_t, (NES_W // 2 - end_t.get_width() // 2, 230))


# ============================================================
# GAME OVER SCREEN
# ============================================================
def draw_game_over(surf, font, frame):
    surf.fill(C_BLACK)
    t = font.render("GAME OVER", False, C_WHITE)
    surf.blit(t, (NES_W // 2 - t.get_width() // 2, NES_H // 2 - 20))
    if (frame // 30) % 2 == 0:
        t2 = font.render("PRESS ENTER TO CONTINUE", False, C_LGRAY)
        surf.blit(t2, (NES_W // 2 - t2.get_width() // 2, NES_H // 2 + 10))


# ============================================================
# MAIN GAME CLASS
# ============================================================
class Game:
    def __init__(self):
        pygame.init()
        self.sounds = init_sounds()
        pygame.display.set_caption("Steamed Hams: The Game")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.nes = pygame.Surface((NES_W, NES_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 8, bold=True)
        self.running = True
        self.frame = 0

        # Game state
        self.state = "title"
        self.player = Player(50, 150)

        # Level/cutscene sequence:
        # cutscene0 -> level0 -> cutscene1 -> level1 -> cutscene2 ->
        # level2 -> cutscene3 -> level3 -> cutscene4 -> level4 ->
        # cutscene5 -> cutscene6 -> credits
        self.sequence = [
            ("cutscene", 0),   # Chalmers arrives
            ("level", 0),      # Skinner's house
            ("cutscene", 1),   # Fire/idea
            ("level", 1),      # School hallway
            ("cutscene", 2),   # Window escape / steam
            ("level", 2),      # Street to Krusty Burger
            ("cutscene", 3),   # Serving hamburgers
            ("level", 3),      # Thought bubble
            ("cutscene", 4),   # Dinner dialogue
            ("level", 4),      # House on fire
            ("cutscene", 5),   # Aurora borealis
            ("cutscene", 6),   # Ending
            ("credits", 0),
        ]
        self.seq_index = 0

        # Level creators
        self.level_creators = [
            create_level_house,
            create_level_school,
            create_level_street,
            create_level_thought,
            create_level_house_fire,
        ]

        # Current level/cutscene state
        self.current_level = None
        self.cam_x = 0

        # Cutscene state
        self.cs_data = None
        self.cs_scene_idx = 0
        self.cs_line_idx = 0
        self.cs_char_idx = 0
        self.cs_timer = 0
        self.cs_text_speed = 2  # chars per frame
        self.cs_waiting = False
        self.cs_frame = 0

        # Key debounce
        self.prev_keys = {}

    def key_just_pressed(self, key):
        current = pygame.key.get_pressed()
        was = self.prev_keys.get(key, False)
        return current[key] and not was

    def advance_sequence(self):
        """Move to the next item in the game sequence."""
        self.seq_index += 1
        if self.seq_index >= len(self.sequence):
            self.state = "credits"
            return
        self.start_current_sequence()

    def start_current_sequence(self):
        """Initialize the current sequence item."""
        if self.seq_index >= len(self.sequence):
            self.state = "credits"
            return
        kind, idx = self.sequence[self.seq_index]
        if kind == "cutscene":
            self.start_cutscene(idx)
        elif kind == "level":
            self.start_level(idx)
        elif kind == "credits":
            self.state = "credits"

    def start_cutscene(self, idx):
        """Start a cutscene."""
        self.state = "cutscene"
        self.cs_data = CUTSCENES[idx]
        self.cs_scene_idx = 0
        self.cs_line_idx = 0
        self.cs_char_idx = 0
        self.cs_timer = 0
        self.cs_waiting = False
        self.cs_frame = 0

    def start_level(self, idx):
        """Start a gameplay level."""
        self.state = "playing"
        data = self.level_creators[idx]()
        self.current_level = data
        px, py = data["player_start"]
        self.player.x, self.player.y = float(px), float(py)
        self.player.vx, self.player.vy = 0, 0
        self.player.goals_done = 0
        self.player.current_item_name = ""
        self.player.current_item_icon = None
        self.cam_x = 0

    def run(self):
        while self.running:
            self.frame += 1
            self.handle_events()
            self.update()
            self.draw()
            self.prev_keys = {k: pygame.key.get_pressed()[k]
                              for k in [pygame.K_RETURN, pygame.K_x,
                                        pygame.K_z, pygame.K_SPACE,
                                        pygame.K_ESCAPE, pygame.K_UP]}
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.USEREVENT + 1:
                if "collect_hi" in self.sounds:
                    self.sounds["collect_hi"].play()

    def update(self):
        if self.state == "title":
            self.update_title()
        elif self.state == "cutscene":
            self.update_cutscene()
        elif self.state == "playing":
            self.update_playing()
        elif self.state == "game_over":
            self.update_game_over()
        elif self.state == "credits":
            self.update_credits()

    def update_title(self):
        if self.key_just_pressed(pygame.K_RETURN):
            self.player = Player(50, 150)
            self.seq_index = 0
            self.start_current_sequence()

    def update_cutscene(self):
        self.cs_frame += 1
        if self.cs_data is None:
            self.advance_sequence()
            return

        scene = self.cs_data["scenes"][self.cs_scene_idx]
        lines = scene["lines"]

        if self.cs_waiting:
            # Wait for button press to advance
            if self.key_just_pressed(pygame.K_RETURN) or \
               self.key_just_pressed(pygame.K_x) or \
               self.key_just_pressed(pygame.K_z) or \
               self.key_just_pressed(pygame.K_SPACE):
                self.cs_line_idx += 1
                if self.cs_line_idx >= len(lines):
                    # Next scene
                    self.cs_scene_idx += 1
                    self.cs_line_idx = 0
                    self.cs_char_idx = 0
                    self.cs_waiting = False
                    if self.cs_scene_idx >= len(self.cs_data["scenes"]):
                        # Cutscene done
                        self.advance_sequence()
                        return
                else:
                    self.cs_char_idx = 0
                    self.cs_waiting = False
        else:
            # Reveal text character by character
            current_line = lines[self.cs_line_idx]
            self.cs_timer += 1
            if self.cs_timer >= self.cs_text_speed:
                self.cs_timer = 0
                self.cs_char_idx += 1
                if self.cs_char_idx < len(current_line):
                    ch = current_line[self.cs_char_idx - 1]
                    if ch not in (' ', '\n') and "text" in self.sounds:
                        self.sounds["text"].play()
                if self.cs_char_idx >= len(current_line):
                    self.cs_char_idx = len(current_line)
                    self.cs_waiting = True
            # Allow skipping ahead
            if self.key_just_pressed(pygame.K_RETURN) or \
               self.key_just_pressed(pygame.K_x) or \
               self.key_just_pressed(pygame.K_z) or \
               self.key_just_pressed(pygame.K_SPACE):
                if self.cs_char_idx < len(current_line):
                    self.cs_char_idx = len(current_line)
                    self.cs_waiting = True

    def update_playing(self):
        if self.current_level is None:
            self.advance_sequence()
            return

        keys = pygame.key.get_pressed()
        level = self.current_level

        # Update player
        self.player._jump_sound = False
        self.player._hurt_sound = False
        self.player._collect_sound = False
        self.player.update(keys, level["platforms"], level["width"])

        # Play sounds
        if self.player._jump_sound and "jump" in self.sounds:
            self.sounds["jump"].play()
        if self.player._hurt_sound and "hurt" in self.sounds:
            self.sounds["hurt"].play()

        # Update camera
        target_x = self.player.x - NES_W // 2 + self.player.w // 2
        self.cam_x += (target_x - self.cam_x) * 0.1
        self.cam_x = max(0, min(self.cam_x, level["width"] - NES_W))

        # Update enemies
        for enemy in level["enemies"]:
            enemy.update(level["platforms"])
            # Check collision with player
            if enemy.alive and self.player.rect.colliderect(enemy.rect):
                # If player is falling on top, kill enemy
                if self.player.vy > 0 and \
                   self.player.y + self.player.h - 5 < enemy.y + enemy.h // 2:
                    enemy.alive = False
                    self.player.vy = JUMP_VEL * 0.6
                    self.player.score += 100
                    if "stomp" in self.sounds:
                        self.sounds["stomp"].play()
                else:
                    self.player.take_damage(1)

        # Update NPCs
        for npc in level["npcs"]:
            npc.update()

        # Check item collection
        for item in level["items"]:
            if not item.collected and self.player.rect.colliderect(item.rect):
                item.collected = True
                self.player.inventory.append(item.item_type)
                self.player.score += 250
                if "collect" in self.sounds:
                    self.sounds["collect"].play()
                    if "collect_hi" in self.sounds:
                        pygame.time.set_timer(pygame.USEREVENT + 1, 100, 1)
                self.player.goals_done += 1
                self.player.current_item_name = item.name
                # Set item icon
                icon_map = {
                    "hamburger": lambda s, x, y: draw_hamburger(s, x, y, 8),
                    "key": draw_key,
                    "apron": draw_apron,
                    "wine": draw_wine_bottle,
                    "spray_can": draw_spray_can,
                }
                self.player.current_item_icon = icon_map.get(item.item_type)

        # Check fire hazards
        for fire in level["fires"]:
            if self.player.rect.colliderect(fire.rect):
                self.player.take_damage(1)

        # Check level completion
        exit_x = level.get("exit_x", -1)
        if exit_x > 0:
            if self.player.goals_done >= level["goal_count"]:
                # Exit is open - complete when reaching it
                if self.player.x >= exit_x - 2:
                    self.advance_sequence()
                    return
            else:
                # Exit is blocked - wall barrier
                if self.player.x >= exit_x - 4:
                    self.player.x = exit_x - 4
        else:
            # No exit - complete when all items collected
            all_collected = all(i.collected for i in level["items"])
            if all_collected:
                self.advance_sequence()
                return

        # Check game over
        if self.player.lives <= 0 and self.player.health <= 0:
            self.state = "game_over"

    def update_game_over(self):
        if self.key_just_pressed(pygame.K_RETURN):
            self.player = Player(50, 150)
            self.state = "title"

    def update_credits(self):
        if self.key_just_pressed(pygame.K_RETURN):
            self.player = Player(50, 150)
            self.state = "title"

    def draw(self):
        self.nes.fill(C_BLACK)

        if self.state == "title":
            draw_title_screen(self.nes, self.font, self.frame)
        elif self.state == "cutscene":
            self.draw_cutscene()
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "game_over":
            draw_game_over(self.nes, self.font, self.frame)
        elif self.state == "credits":
            draw_credits(self.nes, self.font, self.player, self.frame)

        # Scale NES surface to window
        scaled = pygame.transform.scale(self.nes, (WIN_W, WIN_H))
        self.screen.blit(scaled, (0, 0))

        # Scanline effect
        if not hasattr(self, '_scanlines'):
            self._scanlines = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            for y in range(0, WIN_H, SCALE):
                pygame.draw.line(self._scanlines, (0, 0, 0, 40),
                                 (0, y + SCALE - 1), (WIN_W, y + SCALE - 1), 1)
        self.screen.blit(self._scanlines, (0, 0))

        pygame.display.flip()

    def draw_cutscene(self):
        if self.cs_data is None:
            return
        scene = self.cs_data["scenes"][self.cs_scene_idx]
        # Draw illustration
        draw_cutscene_illustration(self.nes, scene["draw"], self.cs_frame)

        # Draw dialogue text
        lines = scene["lines"]
        if self.cs_line_idx < len(lines):
            text = lines[self.cs_line_idx][:self.cs_char_idx]
            # Render multi-line text
            y = 150
            for line in text.split("\n"):
                rendered = self.font.render(line, False, C_WHITE)
                tw = rendered.get_width()
                self.nes.blit(rendered, (NES_W // 2 - tw // 2, y))
                y += 12

        # Draw "press button" indicator
        if self.cs_waiting and (self.cs_frame // 15) % 2 == 0:
            indicator = self.font.render(">>", False, C_WHITE)
            self.nes.blit(indicator, (NES_W - 24, NES_H - 16))

    def draw_playing(self):
        if self.current_level is None:
            return
        level = self.current_level

        # Draw background
        level["draw_bg"](self.nes, int(self.cam_x), level)

        # Draw border if specified
        if level.get("border_color"):
            bc = level["border_color"]
            pygame.draw.rect(self.nes, bc, (0, 0, NES_W, PLAY_H), 3)

        # Draw platforms (only visible ones)
        for plat in level["platforms"]:
            plat.draw(self.nes, int(self.cam_x))

        # Draw fire hazards
        for fire in level["fires"]:
            fire.draw(self.nes, int(self.cam_x))

        # Draw items
        for item in level["items"]:
            item.draw(self.nes, int(self.cam_x))

        # Draw NPCs
        for npc in level["npcs"]:
            npc.draw(self.nes, int(self.cam_x))

        # Draw enemies
        for enemy in level["enemies"]:
            enemy.draw(self.nes, int(self.cam_x))

        # Draw player
        self.player.draw(self.nes, int(self.cam_x))

        # Draw HUD
        draw_hud(self.nes, self.player, self.font)

        # Draw exit indicator and goal hint
        exit_x = level.get("exit_x", -1)
        if exit_x > 0:
            ex_screen = int(exit_x - self.cam_x)
            if 0 <= ex_screen <= NES_W:
                if self.player.goals_done >= level["goal_count"]:
                    # Open - green glow
                    if (self.frame // 10) % 2 == 0:
                        pygame.draw.rect(self.nes, C_GREEN,
                                         (ex_screen - 2, PLAY_H - 50, 24, 42), 1)
                else:
                    # Locked
                    pygame.draw.rect(self.nes, C_RED,
                                     (ex_screen - 2, PLAY_H - 50, 24, 42), 1)

            if self.player.x >= exit_x - 60:
                if self.player.goals_done < level["goal_count"]:
                    remaining = level["goal_count"] - self.player.goals_done
                    hint = self.font.render(
                        f"NEED {remaining} MORE ITEM(S)!", False, C_FIRE_Y)
                    self.nes.blit(hint,
                                  (NES_W // 2 - hint.get_width() // 2, 8))


# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    game = Game()
    game.run()
