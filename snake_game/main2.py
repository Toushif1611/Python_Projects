import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
FPS_BASE = 10

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Levels")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Border settings
BORDER_WIDTH = 5

# Font
font = pygame.font.SysFont(None, 35)
big_font = pygame.font.SysFont(None, 50)

# Levels configuration
LEVELS = [
    {"obstacles": [], "speed": 10, "food_count": 1, "name": "Level 1"},
    {"obstacles": [(200, 200), (200, 220), (200, 240), (200, 260), (200, 280)], "speed": 11, "food_count": 1, "name": "Level 2"},
    {"obstacles": [(200, 200), (200, 220), (200, 240), (200, 260), (200, 280), (600, 200), (600, 220), (600, 240), (600, 260), (600, 280)], "speed": 12, "food_count": 1, "name": "Level 3"},
    {"obstacles": [(200, 200), (200, 220), (200, 240), (200, 260), (200, 280), (600, 200), (600, 220), (600, 240), (600, 260), (600, 280), (400, 100), (420, 100), (440, 100), (460, 100), (380, 120), (420, 120)], "speed": 13, "food_count": 1, "name": "Level 4"},
    {"obstacles": [(200, 200), (200, 220), (200, 240), (200, 260), (200, 280), (600, 200), (600, 220), (600, 240), (600, 260), (600, 280), (400, 100), (420, 100), (440, 100), (460, 100), (380, 120), (420, 120), (300, 400), (320, 400), (340, 400), (360, 400), (380, 400), (280, 420), (340, 420)], "speed": 14, "food_count": 1, "name": "Level 5"}
]

def draw_snake(snake_body):
    for block in snake_body:
        pygame.draw.rect(screen, GREEN, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def draw_food(food_pos):
    pygame.draw.rect(screen, RED, [food_pos[0], food_pos[1], BLOCK_SIZE, BLOCK_SIZE])

def draw_obstacles(obstacles):
    for obs in obstacles:
        pygame.draw.rect(screen, BLUE, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])

def draw_score(score, level):
    text = font.render("Score: " + str(score) + " | Level: " + str(level + 1), True, WHITE)
    screen.blit(text, [10, 10])

def draw_pause_indicator(paused):
    if paused:
        pause_indicator = font.render("PAUSED - Press P to Resume", True, YELLOW)
        screen.blit(pause_indicator, [WIDTH / 2 - 120, 10])

def draw_border():
    # Draw border around the play area
    pygame.draw.line(screen, YELLOW, [BORDER_WIDTH, BORDER_WIDTH], [WIDTH - BORDER_WIDTH, BORDER_WIDTH], BORDER_WIDTH)
    pygame.draw.line(screen, YELLOW, [BORDER_WIDTH, BORDER_WIDTH], [BORDER_WIDTH, HEIGHT - BORDER_WIDTH], BORDER_WIDTH)
    pygame.draw.line(screen, YELLOW, [WIDTH - BORDER_WIDTH, BORDER_WIDTH], [WIDTH - BORDER_WIDTH, HEIGHT - BORDER_WIDTH], BORDER_WIDTH)
    pygame.draw.line(screen, YELLOW, [BORDER_WIDTH, HEIGHT - BORDER_WIDTH], [WIDTH - BORDER_WIDTH, HEIGHT - BORDER_WIDTH], BORDER_WIDTH)

def show_menu():
    menu = True
    selected_option = 0
    options = ["Start Game", "Instructions", "Quit"]

    while menu:
        screen.fill(BLACK)

        # Title
        title_text = big_font.render("SNAKE GAME", True, GREEN)
        screen.blit(title_text, [WIDTH / 2 - 120, HEIGHT / 4])

        # Menu options
        for i, option in enumerate(options):
            color = WHITE if i != selected_option else GREEN
            option_text = font.render(option, True, color)
            screen.blit(option_text, [WIDTH / 2 - 80, HEIGHT / 2 + i * 50])

        # Instructions
        if selected_option == 1:  # Instructions
            instr_text1 = font.render("Use arrow keys to move", True, YELLOW)
            instr_text2 = font.render("Eat food to score points", True, YELLOW)
            instr_text3 = font.render("Avoid walls and obstacles", True, YELLOW)
            instr_text4 = font.render("Press P to pause/continue", True, RED)
            screen.blit(instr_text1, [WIDTH / 2 - 120, HEIGHT / 2 + 200])
            screen.blit(instr_text2, [WIDTH / 2 - 120, HEIGHT / 2 + 230])
            screen.blit(instr_text3, [WIDTH / 2 - 120, HEIGHT / 2 + 260])
            screen.blit(instr_text4, [WIDTH / 2 - 120, HEIGHT / 2 + 170])

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:  # Start Game
                        menu = False
                        return "start"
                    elif selected_option == 1:  # Instructions
                        # Show detailed instructions
                        pass
                    elif selected_option == 2:  # Quit
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_SPACE and selected_option == 1:
                    # Return to menu from instructions
                    pass

    return "start"

def game_loop():
    level = 0
    current_level = LEVELS[level]
    current_speed = LEVELS[0]["speed"]
    current_food_count = LEVELS[0]["food_count"]
    obstacles = LEVELS[level]["obstacles"]
    fps = current_speed
    food_count = current_food_count

    game_over = False
    game_close = False
    game_lost = False
    paused = False

    # Initial snake position and body
    x = WIDTH / 2
    y = HEIGHT / 2
    x_change = 0
    y_change = 0
    snake_body = []
    length_of_snake = 1

    # Food positions
    foods = []
    for _ in range(food_count):
        food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        # Ensure food not on obstacles or snake
        while (food_x, food_y) in obstacles or (food_x, food_y) in [(b[0], b[1]) for b in snake_body]:
            food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
        foods.append([food_x, food_y])

    score = 0

    while not game_over:
        while game_close:
            screen.fill(BLACK)
            if game_lost:
                level_text = big_font.render("You Lose!", True, RED)
                screen.blit(level_text, [WIDTH / 2 - 100, HEIGHT / 3])
                message = font.render("Press R-Retry or Q-Quit", True, WHITE)
                screen.blit(message, [WIDTH / 2 - 120, HEIGHT / 2])
            else:
                level_text = big_font.render(current_level["name"] + " Complete!", True, GREEN)
                screen.blit(level_text, [WIDTH / 2 - 150, HEIGHT / 3])
                message = font.render("Press C-Continue or Q-Quit", True, RED)
                screen.blit(message, [WIDTH / 2 - 120, HEIGHT / 2])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_r and game_lost:
                        # Retry the current level
                        game_lost = False
                        score = 0
                        x = WIDTH / 2
                        y = HEIGHT / 2
                        x_change = 0
                        y_change = 0
                        snake_body = []
                        length_of_snake = 1
                        foods = []
                        for _ in range(food_count):
                            food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                            food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                            while (food_x, food_y) in obstacles or (food_x, food_y) in [(b[0], b[1]) for b in snake_body]:
                                food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                                food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                            foods.append([food_x, food_y])
                        game_close = False
                    if event.key == pygame.K_c and not game_lost:
                        if level < 4:
                            level += 1
                            current_level = LEVELS[level]
                            obstacles = current_level["obstacles"]
                            fps = current_level["speed"]
                            # Reset snake length and position for new level
                            score = 0
                            x = WIDTH / 2
                            y = HEIGHT / 2
                            x_change = 0
                            y_change = 0
                            snake_body = []
                            length_of_snake = 1
                            foods = []
                            for _ in range(food_count):
                                food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                                food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                                while (food_x, food_y) in obstacles or (food_x, food_y) in [(b[0], b[1]) for b in snake_body]:
                                    food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                                    food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                                foods.append([food_x, food_y])
                            game_close = False
                        else:
                            # Game completed
                            screen.fill(BLACK)
                            win_text = big_font.render("You Won All Levels!", True, GREEN)
                            screen.blit(win_text, [WIDTH / 2 - 150, HEIGHT / 2])
                            pygame.display.update()
                            pygame.time.delay(3000)
                            game_over = True
                            game_close = False

        # Pause handling
        while paused and not game_over:
            screen.fill(BLACK)
            pause_text = big_font.render("PAUSED", True, YELLOW)
            screen.blit(pause_text, [WIDTH / 2 - 80, HEIGHT / 3])
            resume_text = font.render("Press P to Resume", True, WHITE)
            screen.blit(resume_text, [WIDTH / 2 - 90, HEIGHT / 2])
            menu_text = font.render("Press M for Menu", True, WHITE)
            screen.blit(menu_text, [WIDTH / 2 - 80, HEIGHT / 2 + 30])
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    elif event.key == pygame.K_m:
                        return "start"  # Return to menu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -BLOCK_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = BLOCK_SIZE
                    x_change = 0

        x += x_change
        y += y_change

        # Border collision check
        if x <= BORDER_WIDTH or x >= WIDTH - BORDER_WIDTH - BLOCK_SIZE or y <= BORDER_WIDTH or y >= HEIGHT - BORDER_WIDTH - BLOCK_SIZE:
            game_close = True
            game_lost = True

        # Obstacle check
        if (x, y) in obstacles:
            game_close = True
            game_lost = True

        screen.fill(BLACK)
        draw_border()
        draw_obstacles(obstacles)

        # Snake head
        snake_head = [x, y]
        snake_body.append(snake_head)

        if len(snake_body) > length_of_snake:
            del snake_body[0]

        # Self collision
        for block in snake_body[:-1]:
            if block == snake_head:
                game_close = True
                game_lost = True

        draw_snake(snake_body)

        # Draw all foods
        for food in foods[:]:
            draw_food(food)
            if x == food[0] and y == food[1]:
                foods.remove(food)
                length_of_snake += 1
                score += 1
                
                # Spawn new food if score < 10 (level not complete)
                if score < 10:
                    food_x = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, WIDTH - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                    food_y = round(random.randrange(BORDER_WIDTH + BLOCK_SIZE, HEIGHT - BORDER_WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                    while (food_x, food_y) in obstacles or (food_x, food_y) in [(b[0], b[1]) for b in snake_body]:
                        food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                        food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                    foods.append([food_x, food_y])

        draw_score(score, level)
        draw_pause_indicator(paused)

        pygame.display.update()

        # Check if level complete
        if score >= 10:
            game_close = True

        clock.tick(fps)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    while True:
        choice = show_menu()
        if choice == "start":
            game_loop()
