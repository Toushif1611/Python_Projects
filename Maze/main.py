import pygame
import sys
import random
import asyncio
import json
import os

pygame.init()

# ------------------ CONSTANTS ------------------
WIDTH, HEIGHT = 700, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE  = (50, 150, 255)
GREEN = (0, 255, 0)
RED   = (200, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

FPS = 60
MAX_MAZE_SIZE = 41

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")
pygame.mixer.init()  # For potential sound effects later

font = pygame.font.Font(None, 30)
big_font = pygame.font.Font(None, 50)

# ------------------ MAZE GENERATOR ------------------
def create_level(level):
    size = min(13 + (level * 2), MAX_MAZE_SIZE)

    if size % 2 == 0:
        size += 1

    rows = cols = size
    cell_size = min(WIDTH // cols, HEIGHT // rows)

    maze = [[1] * cols for _ in range(rows)]
    directions = [(-2,0),(2,0),(0,-2),(0,2)]

    def generate(r, c):
        maze[r][c] = 0
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows-1 and 0 < nc < cols-1 and maze[nr][nc] == 1:
                maze[r + dr//2][c + dc//2] = 0
                generate(nr, nc)

    generate(1, 1)

    goal_r, goal_c = rows - 2, cols - 2
    maze[goal_r][goal_c] = 0

    # Ensure goal is reachable
    neighbors = [
        (goal_r-1, goal_c),
        (goal_r+1, goal_c),
        (goal_r, goal_c-1),
        (goal_r, goal_c+1)
    ]

    if not any(
        0 <= r < rows and 0 <= c < cols and maze[r][c] == 0
        for r, c in neighbors
    ):
        r, c = neighbors[0]
        maze[r][c] = 0

    return maze, rows, cols, cell_size, goal_r, goal_c

# ------------------ PLAYER CLASS ------------------
class Player:
    def __init__(self, cell_size, speed):
        self.cell_size = cell_size
        self.speed = speed
        self.reset()

    def reset(self):
        self.x = self.cell_size
        self.y = self.cell_size
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False

    def update(self):
        if not self.moving:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        if dx != 0:
            self.x += self.speed * (1 if dx > 0 else -1)
            if abs(dx) <= self.speed:
                self.x = self.target_x

        if dy != 0:
            self.y += self.speed * (1 if dy > 0 else -1)
            if abs(dy) <= self.speed:
                self.y = self.target_y

        if self.x == self.target_x and self.y == self.target_y:
            self.moving = False

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE,
                        (self.x, self.y,
                         self.cell_size, self.cell_size))

# ------------------ GAME INIT ------------------
level = 1
maze, ROWS, COLS, CELL_SIZE, goal_row, goal_col = create_level(level)
player = Player(CELL_SIZE, 4 + level)

async def main():
    global level, maze, ROWS, COLS, CELL_SIZE
    global goal_row, goal_col, player, game_over, new_high_score

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(WHITE)
        
        # ------------------ EVENTS ------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:  # Restart
                        reset_game()
                    elif event.key == pygame.K_m:  # Menu/Quit
                        running = False

        keys = pygame.key.get_pressed()

        # ------------------ INPUT ------------------
        if not player.moving:
            row = player.y // CELL_SIZE
            col = player.x // CELL_SIZE
            new_row, new_col = row, col

            if keys[pygame.K_UP]:
                new_row -= 1
            elif keys[pygame.K_DOWN]:
                new_row += 1
            elif keys[pygame.K_LEFT]:
                new_col -= 1
            elif keys[pygame.K_RIGHT]:
                new_col += 1

            if (0 <= new_row < ROWS and
                0 <= new_col < COLS and
                maze[new_row][new_col] == 0):

                player.target_x = new_col * CELL_SIZE
                player.target_y = new_row * CELL_SIZE
                player.moving = True

        # ------------------ UPDATE ------------------
        player.update()

        # ------------------ WIN CHECK ------------------
        if (player.y // CELL_SIZE == goal_row and
            player.x // CELL_SIZE == goal_col):

            level += 1
            maze, ROWS, COLS, CELL_SIZE, goal_row, goal_col = create_level(level)
            player = Player(CELL_SIZE, min(4 + level, 12))

        # ------------------ DRAW MAZE ------------------
        for r in range(ROWS):
            for c in range(COLS):
                color = WHITE if maze[r][c] == 0 else BLACK
                pygame.draw.rect(screen, color,
                               (c * CELL_SIZE, r * CELL_SIZE,
                                CELL_SIZE, CELL_SIZE))

        # Goal
        pygame.draw.rect(screen, GREEN,
                        (goal_col * CELL_SIZE,
                         goal_row * CELL_SIZE,
                         CELL_SIZE, CELL_SIZE))

        # Player
        player.draw(screen)

        # ------------------ HUD ------------------
        level_text = font.render(f"Level: {level}", True, RED)
        screen.blit(level_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()

# ------------------ RUN ------------------
if sys.platform == "emscripten":
    asyncio.ensure_future(main())
else:
    asyncio.run(main())
