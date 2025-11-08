# super_snake.py
# Requirements: pygame. Optional: numpy (for synthesized fallback beep if eat.wav missing).

import pygame
import random
import sys
import os
import math

# Try to import numpy for fallback beep synthesis (optional)
try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:
    _HAS_NUMPY = False

# ---- Audio pre-init to avoid common sound issues ----
# try to put sensible defaults so Sound.play() works reliably on most systems
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# ---- Config ----
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 15              # snake speed
WINDOW_CAPTION = "Super Snake V1.1 by Sir-Slowpoke"

# Shake settings (pixels)
SHAKE_DURATION = 0.3  # seconds
SHAKE_INTENSITY = 100   # max pixels

# Colors (R,G,B)
WHITE = (200, 90, 40)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
DARK_GREEN = (0, 120, 0)
GREEN = (0, 150, 0)
RED = (200, 25, 0)
YELLOW = (200, 200, 0)

# ---- Helpers ----
def draw_text_center(surface, text, size, color, y):
    font = pygame.font.SysFont(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)

def random_food(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos

def draw_cell(surface, pos, color):
    rect = pygame.Rect(pos[0]*CELL_SIZE, pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)

# Synthesise a short beep using numpy (if available) for fallback
def make_beep_sound(freq=880, duration_ms=150, volume=0.25, sample_rate=44100):
    if not _HAS_NUMPY:
        return None
    t = np.linspace(0, duration_ms/1000.0, int(sample_rate * duration_ms/1000.0), False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    # apply short envelope to avoid clicks
    env_len = max(1, int(0.01 * sample_rate))  # 10ms envelope
    env = np.ones_like(wave)
    attack = np.linspace(0, 1, env_len)
    decay = np.linspace(1, 0, env_len)
    env[:env_len] = attack
    env[-env_len:] = decay
    wave *= env
    stereo = np.column_stack((wave, wave))
    arr = np.int16(stereo * 32767 * volume)
    try:
        return pygame.sndarray.make_sound(arr.copy())
    except Exception:
        return None

# Load eat sound with robust handling
def load_eat_sound(path="eat.wav"):
    # attempt to load the file if present
    if os.path.isfile(path):
        try:
            s = pygame.mixer.Sound(path)
            # lower volume slightly so it's not jarring
            s.set_volume(0.7)
            return s
        except Exception as e:
            print("Warning: failed to load eat.wav:", e)
    # fallback: try to synthesise if numpy is available
    fallback = make_beep_sound(freq=700, duration_ms=100, volume=0.50)
    if fallback:
        print("Using synthesized beep (numpy) as fallback audio.")
        return fallback
    print("No eat.wav and no numpy fallback available. Sound disabled.")
    return None

# ---- Game ----
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(WINDOW_CAPTION)
    clock = pygame.time.Clock()

    # create a separate surface to render the game scene onto
    game_surf = pygame.Surface((WIDTH, HEIGHT))

    # load sound
    eat_sound = load_eat_sound("eat.wav")

    # start screen
    in_start = True
    while in_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("GAME_START_EVENT")
                    in_start = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.fill(DARK_GRAY)
        draw_text_center(screen, "SUPER SNAKE", 64, YELLOW, HEIGHT//3)
        draw_text_center(screen, "Press SPACE to start", 28, WHITE, HEIGHT//2)
        pygame.display.flip()
        clock.tick(30)

    # game init
    snake = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
    # start with three segments heading right for nicer feel
    snake = [(GRID_WIDTH//2 - 1, GRID_HEIGHT//2), (GRID_WIDTH//2, GRID_HEIGHT//2)]
    direction = (1, 0)
    next_direction = direction
    food = random_food(snake)
    score = 0
    game_over = False

    # shake state
    shake_time = 0.0
    shake_duration = SHAKE_DURATION
    shake_intensity = SHAKE_INTENSITY

    while True:
        dt = clock.tick(FPS) / 1000.0  # seconds elapsed (helps with smooth shake decay)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if direction != (0, 1): next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if direction != (0, -1): next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if direction != (1, 0): next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if direction != (-1, 0): next_direction = (1, 0)
                elif event.key == pygame.K_r and game_over:
                    # restart cleanly
                    snake = [(GRID_WIDTH//2 - 1, GRID_HEIGHT//2), (GRID_WIDTH//2, GRID_HEIGHT//2)]
                    direction = (1, 0)
                    next_direction = direction
                    food = random_food(snake)
                    score = 0
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        # update
        if not game_over:
            # commit direction (prevents immediate 180-degree flips)
            if (next_direction[0] * -1, next_direction[1] * -1) != direction:
                direction = next_direction

            head_x, head_y = snake[-1]
            new_head = (head_x + direction[0], head_y + direction[1])

            # collisions
            if (new_head in snake) or not (0 <= new_head[0] < GRID_WIDTH) or not (0 <= new_head[1] < GRID_HEIGHT):
                game_over = True
            else:
                snake.append(new_head)
                if new_head == food:
                    score += 1
                    food = random_food(snake)
                    # play sound (non-blocking)
                    if eat_sound:
                        try:
                            eat_sound.play()
                        except Exception as e:
                            print("Audio play failed:", e)
                    # start shake
                    shake_time = shake_duration
                else:
                    # normal move
                    snake.pop(0)

        # decay shake
        if shake_time > 0:
            shake_time = max(0.0, shake_time - dt)

        # compute shake offset (pixels) using decaying amplitude; random each frame for jitter
        if shake_time > 0:
            frac = shake_time / shake_duration  # 1 -> 0
            # smoother decay curve
            amp = shake_intensity * (0.12)   # quadratic decay to look nicer
            offset_x = int(random.uniform(-1.0, 1.0) * amp)
            offset_y = int(random.uniform(1.0, -1.0) * amp)
        else:
            offset_x = 0
            offset_y = 0

        # draw everything onto game_surf
        game_surf.fill(BLACK)

        # optional faint grid lines for visual clarity (won't be affected by numeric shifting)
        # (comment this out if you want a cleaner look)
        # for gx in range(0, WIDTH, CELL_SIZE):
        #     pygame.draw.line(game_surf, DARK_GRAY, (gx, 0), (gx, HEIGHT))
        # for gy in range(0, HEIGHT, CELL_SIZE):
        #     pygame.draw.line(game_surf, DARK_GRAY, (0, gy), (WIDTH, gy))

        # draw food & snake onto game_surf (grid coordinates)
        draw_cell(game_surf, food, RED)
        for i, part in enumerate(snake):
            color = GREEN if i == len(snake)-1 else DARK_GREEN
            draw_cell(game_surf, part, color)

        # HUD
        draw_text_center(game_surf, f"Score: {score}", 28, WHITE, 20)
        if game_over:
            draw_text_center(game_surf, "The end", 64, RED, HEIGHT//2 - 20)
            draw_text_center(game_surf, "Press R to restart", 28, WHITE, HEIGHT//2 + 30)

        # Now blit the game_surf to the main screen with the shake offset.
        # We also ensure we don't blit outside the window by clamping coordinates.
        blit_x = offset_x
        blit_y = offset_y
        # center the surface normally when no offset (it's already top-left aligned),
        # we simply allow small shifts around (0,0). If desired, you could center the game surface in a larger window.
        screen.fill(DARK_GRAY)  # background behind the offset surface
        screen.blit(game_surf, (blit_x, blit_y))
        pygame.display.flip()

# entry
if __name__ == "__main__":
    main()
    "MADE BY SIR-SLOWPOKE, 2025"