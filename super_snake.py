"""
super_snake.py
Simple Snake game using Pygame.

- Start screen: "Super Snake" — press SPACE to start
- Controls: Arrow keys or WASD.
- Restart: press R.
- Quit: Esc.
"""

import pygame
import random
import sys

# --- Config ---
CELL_SIZE = 20
GRID_WIDTH = 30   # results in window width = CELL_SIZE * GRID_WIDTH
GRID_HEIGHT = 30  # results in window height = CELL_SIZE * GRID_HEIGHT
WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 15      # snake speed (increase for harder game)

# Colors (R,G,B)
WHITE = (200, 90, 40)
BLACK = (0, 0, 0)
DARK_GRAY = (30, 30, 30)
GREEN = (0, 150, 0)
RED = (200, 25, 0)
YELLOW = (200, 200, 0)

# --- Helper functions ---
def random_food_position(snake):
    """Return a random grid position not occupied by snake (tuple x,y)."""
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in snake:
            return (x, y)

def draw_text_center(surface, text, size, color, y):
    font = pygame.font.SysFont(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(WIDTH // 2, y))
    surface.blit(rendered, rect)

def draw_cell(surface, pos, color):
    rect = pygame.Rect(pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)

# --- Game logic ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Super Snake")
    clock = pygame.time.Clock()

    # Start screen
    in_start_screen = True
    while in_start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Trigger the start event (user wanted an output on space)
                    print("GAME_START_EVENT")
                    in_start_screen = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.fill(DARK_GRAY)
        draw_text_center(screen, "SUPER SNAKE", 64, YELLOW, HEIGHT // 3)
        draw_text_center(screen, "Press SPACE to start", 28, WHITE, HEIGHT // 2)
        draw_text_center(screen, "Arrows or WASD to move. Esc to quit.", 20, WHITE, HEIGHT // 2 + 40)
        pygame.display.flip()
        clock.tick(30)

    # Initialize snake
    snake = [(GRID_WIDTH // 2 + i, GRID_HEIGHT // 2) for i in range(3)][::-1]  # head is last element
    direction = (-1, 0)  # moving left initially
    next_direction = direction
    food = random_food_position(snake)
    score = 0
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    next_direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    next_direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    next_direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    next_direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_SPACE and not game_over:
                    # optional: allow pausing/resuming with space during play
                    print("SPACE_PRESSED_IN_GAME")
                elif event.key == pygame.K_r and game_over:
                    # restart: reinitialize everything
                    snake = [(GRID_WIDTH // 2 + i, GRID_HEIGHT // 2) for i in range(3)][::-1]
                    direction = (-1, 0)
                    next_direction = direction
                    food = random_food_position(snake)
                    score = 0
                    game_over = False

        if not running:
            break

        if not game_over:
            # Prevent reversing direction directly
            if (next_direction[0] * -1, next_direction[1] * -1) != direction:
                direction = next_direction

            # Move snake
            head_x, head_y = snake[-1]
            new_head = (head_x + direction[0], head_y + direction[1])

            # Check wall collisions
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
                game_over = True
            # Check self collision
            elif new_head in snake:
                game_over = True
            else:
                snake.append(new_head)
                # Check food
                if new_head == food:
                    score += 1
                    food = random_food_position(snake)
                else:
                    snake.pop(0)  # move forward

        # Draw
        screen.fill(BLACK)
        # grid optional faint lines
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, DARK_GRAY, (0, y), (WIDTH, y))

        # Draw food and snake
        draw_cell(screen, food, RED)
        for i, part in enumerate(snake):
            color = GREEN if i == len(snake) - 1 else (0, 160, 0)  # head brighter
            draw_cell(screen, part, color)

        # HUD
        font = pygame.font.SysFont(None, 25)
        score_surf = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_surf, (8, 8))

        if game_over:
            draw_text_center(screen, "GAME OVER", 64, RED, HEIGHT // 2 - 20)
            draw_text_center(screen, f"Score: {score}  —  Press R to restart or Esc to quit", 24, WHITE, HEIGHT // 2 + 30)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print("Exited game.")

if __name__ == "__main__":
    main()
    "MADE BY SIR-SLOWPOKE, 2025"