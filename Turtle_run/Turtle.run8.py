# Turtle Run - Restart Version
# by Toushif1611 (Updated)

import turtle
import random

# -----------------------
# CONSTANTS
# -----------------------
WIDTH, HEIGHT = 700, 700
BORDER = 290

# -----------------------
# GLOBAL VARIABLES
# -----------------------
score = 0
level = 1
game_over = False
food_dx = 2
food_dy = 2

# -----------------------
# SCREEN SETUP
# -----------------------
screen = turtle.Screen()
screen.setup(WIDTH, HEIGHT)
screen.bgcolor("black")
screen.title("TURTLE RUN")
screen.tracer(0)

# -----------------------
# BORDER
# -----------------------
border_pen = turtle.Turtle()
border_pen.color("white")
border_pen.pensize(3)
border_pen.penup()
border_pen.goto(-300, -300)
border_pen.pendown()
for _ in range(4):
    border_pen.forward(600)
    border_pen.left(90)
border_pen.hideturtle()

# -----------------------
# PLAYER
# -----------------------
player = turtle.Turtle()
player.shape("turtle")
player.color("green")
player.penup()
player.speed(0)
player.goto(0, 0)
player.setheading(90)

base_speed = 3             # nominal forward speed
rotate_speed = 4

# movement flags (for smooth input handling)
turn_left_pressed = False
turn_right_pressed = False
accel_pressed = False

# -----------------------
# FOOD
# -----------------------
food = turtle.Turtle()
food.shape("circle")
food.color("red")
food.penup()
food.speed(0)

def respawn_food():
    food.goto(random.randint(-BORDER, BORDER),
              random.randint(-BORDER, BORDER))
respawn_food()

# -----------------------
# SCORE DISPLAY
# -----------------------
pen = turtle.Turtle()
pen.hideturtle()
pen.color("white")
pen.penup()
pen.goto(-290, 310)

def update_score():
    pen.clear()
    pen.write(f"Score: {score}  Level: {level}",
              align="left",
              font=("Courier", 18, "normal"))

update_score()

# -----------------------
# CONTROLS (smooth)
# -----------------------

def start_turn_left():
    global turn_left_pressed
    turn_left_pressed = True

def stop_turn_left():
    global turn_left_pressed
    turn_left_pressed = False

def start_turn_right():
    global turn_right_pressed
    turn_right_pressed = True

def stop_turn_right():
    global turn_right_pressed
    turn_right_pressed = False

def start_accel():
    global accel_pressed
    accel_pressed = True

def stop_accel():
    global accel_pressed
    accel_pressed = False

screen.listen()
# arrow keys set/clear flags
screen.onkeypress(start_turn_left, "Left")
screen.onkeyrelease(stop_turn_left, "Left")
screen.onkeypress(start_turn_right, "Right")
screen.onkeyrelease(stop_turn_right, "Right")
# Up toggles faster forward motion
screen.onkeypress(start_accel, "Up")
screen.onkeyrelease(stop_accel, "Up")

# -----------------------
# RESTART FUNCTION
# -----------------------
def restart_game():
    global score, level, game_over, food_dx, food_dy

    # only allow a restart when the game is over
    if not game_over:
        return

    # clear any messages written by previous game
    pen.clear()

    score = 0
    level = 1
    game_over = False
    food_dx = 2
    food_dy = 2
    player.goto(0,0)
    player.setheading(90)
    respawn_food()
    update_score()
    pen.goto(-290,310)
    game_loop()

# -----------------------
# GAME LOOP
# -----------------------
def game_loop():
    global score, level, food_dx, food_dy, game_over

    if game_over:
        return

    # Continuous forward movement (modify speed when accelerating)
    curr_speed = base_speed * (2 if accel_pressed else 1)
    player.forward(curr_speed)

    # turning when keys held
    if turn_left_pressed:
        player.left(rotate_speed)
    if turn_right_pressed:
        player.right(rotate_speed)

    # Border restriction
    x, y = player.xcor(), player.ycor()
    if x > BORDER: player.setx(BORDER)
    if x < -BORDER: player.setx(-BORDER)
    if y > BORDER: player.sety(BORDER)
    if y < -BORDER: player.sety(-BORDER)

    # Collision
    if player.distance(food) < 20:
        score += 1
        respawn_food()

    # Level system
    level = min(5, score // 10 + 1)

    # Food movement
    if level >= 2:
        food.setx(food.xcor() + food_dx * level/2)
        food.sety(food.ycor() + food_dy * level/2)
        if food.xcor() > BORDER or food.xcor() < -BORDER:
            food_dx *= -1
        if food.ycor() > BORDER or food.ycor() < -BORDER:
            food_dy *= -1

    update_score()

    # Win condition
    if score >= 50:
        game_over = True
        pen.goto(0, 0)
        pen.write("YOU WIN!", align="center",
                  font=("Courier", 40, "bold"))

        # Show restart instruction
        pen.goto(0, -50)
        pen.write("Press 'R' to Restart", align="center",
                  font=("Courier", 20, "normal"))

        # force a screen update so messages appear immediately
        screen.update()
        return

    screen.update()
    screen.ontimer(game_loop, 16)  # ~60 FPS

# -----------------------
# KEYBIND RESTART
# -----------------------
screen.onkeypress(restart_game, "r")

# -----------------------
# START GAME
# -----------------------
game_loop()
screen.mainloop()