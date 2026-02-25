# Space Invader
# by Toushif1611
# Add level system

import turtle
import math

# -----------------------
# Screen Setup
# -----------------------
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Space Invader")
screen.setup(700, 700)
screen.tracer(0)

# -----------------------
# Border
# -----------------------
border = turtle.Turtle()
border.hideturtle()
border.color("white")
border.pensize(3)
border.penup()
border.goto(-300, -300)
border.pendown()
for _ in range(4):
    border.forward(600)
    border.left(90)

# -----------------------
# Score
# -----------------------
score = 0

score_pen = turtle.Turtle()
score_pen.hideturtle()
score_pen.color("white")
score_pen.penup()
score_pen.goto(-290, 280)

def update_score():
    score_pen.clear()
    score_pen.write(f"Score: {score}", font=("Arial", 14, "normal"))

update_score()

# -----------------------
# Player
# -----------------------
player = turtle.Turtle()
player.shape("triangle")
player.color("blue")
player.penup()
player.setheading(90)
player.goto(0, -250)

player_speed = 20

def move_left():
    x = player.xcor() - player_speed
    if x < -280:
        x = -280
    player.setx(x)

def move_right():
    x = player.xcor() + player_speed
    if x > 280:
        x = 280
    player.setx(x)

# -----------------------
# Enemies
# -----------------------
number_of_enemies = 30
enemies = []

start_x = -225
start_y = 250
count = 0

# -----------------------
# Level System
# -----------------------
level = 1

level_pen = turtle.Turtle()
level_pen.hideturtle()
level_pen.color("white")
level_pen.penup()
level_pen.goto(200, 280)

def update_level():
    level_pen.clear()
    level_pen.write(f"Level: {level}", font=("Arial", 14, "normal"))

update_level()

# -----------------------
# Reset Enemies Function
# -----------------------
def reset_enemies():
    global enemies, enemy_speed
    
    start_x = -225
    start_y = 250
    count = 0

    for enemy in enemies:
        x = start_x + (50 * count)
        y = start_y
        enemy.goto(x, y)

        count += 1
        if count == 10:
            count = 0
            start_y -= 50

    enemy_speed = 2 + level   # increase difficulty

# -----------------------
# Create Enemies
# -----------------------
enemy_speed = 3

for i in range(number_of_enemies):
    enemy = turtle.Turtle()
    enemy.shape("circle")
    enemy.color("red")
    enemy.penup()
    enemy.speed(0)
    enemies.append(enemy)

# Position them for first level
reset_enemies()

# -----------------------
# Bullet
# -----------------------
bullet = turtle.Turtle()
bullet.shape("triangle")
bullet.color("yellow")
bullet.penup()
bullet.setheading(90)
bullet.shapesize(0.5, 0.5)
bullet.hideturtle()

# -----------------------
# Multiple Bullets System
# -----------------------
bullets = []
bullet_speed = 20

def fire_bullet():
    bullet = turtle.Turtle()
    bullet.shape("triangle")
    bullet.color("yellow")
    bullet.penup()
    bullet.setheading(90)
    bullet.shapesize(0.5, 0.5)
    bullet.goto(player.xcor(), player.ycor() + 10)
    bullets.append(bullet)

# -----------------------
# Collision Function
# -----------------------
def is_collision(t1, t2):
    distance = math.hypot(t1.xcor() - t2.xcor(),
                          t1.ycor() - t2.ycor())
    return distance < 20

# -----------------------
# Game Over
# -----------------------
game_over = False
game_over_pen = turtle.Turtle()
game_over_pen.hideturtle()
game_over_pen.color("white")

def show_game_over():
    game_over_pen.goto(0, 0)
    game_over_pen.write("GAME OVER",
                        align="center",
                        font=("Arial", 24, "bold"))

# -----------------------
# Keyboard Bindings
# -----------------------
screen.listen()
screen.onkeypress(move_left, "Left")
screen.onkeypress(move_right, "Right")
screen.onkeypress(fire_bullet, "space")

# -----------------------
# Main Game Loop (Smooth)
# -----------------------
def game_loop():
    global enemy_speed, bullet_state, score, game_over, level

    if game_over:
        return

    move_down = False

    # Move enemies
    for enemy in enemies:
        enemy.setx(enemy.xcor() + enemy_speed)

        if enemy.xcor() > 280 or enemy.xcor() < -280:
            move_down = True

    if move_down:
        enemy_speed *= -1
        for enemy in enemies:
            enemy.sety(enemy.ycor() - 40)

    # -----------------------
    # Move Bullets
    # -----------------------
    for bullet in bullets[:]:
        bullet.sety(bullet.ycor() + bullet_speed)

        if bullet.ycor() > 275:
            bullet.hideturtle()
            bullets.remove(bullet)

    # -----------------------
    # Collision Check
    # -----------------------
    alive_enemies = 0

    for enemy in enemies:

        if enemy.ycor() < -240:
            player.hideturtle()
            show_game_over()
            game_over = True
            return

        # Bullet hit
        for bullet in bullets[:]:
            if is_collision(bullet, enemy):

                bullet.hideturtle()
                bullets.remove(bullet)

                enemy.hideturtle()
                enemy.goto(0, 10000)

                score += 10
                update_score()
                break

        if enemy.ycor() < 1000:
            alive_enemies += 1

        if is_collision(player, enemy):
            player.hideturtle()
            show_game_over()
            game_over = True
            return

    # LEVEL COMPLETE
    if alive_enemies == 0:
        level += 1
        update_level()
        reset_enemies()
        enemy.showturtle()

    screen.update()
    screen.ontimer(game_loop, 16)

# Start game
game_loop()
screen.mainloop()