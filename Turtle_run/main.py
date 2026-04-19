import turtle
import random
import json
import os

# Load high score
highscore_file = os.path.join(os.path.dirname(__file__), '..', 'highscores.json')
if os.path.exists(highscore_file):
    with open(highscore_file, 'r') as f:
        data = json.load(f)
        high_score = data.get('high_score', 0)
else:
    high_score = 0

# Set up screen
s = turtle.Screen()
s.bgcolor("black")
s.title("Turtle Game")
s.setup(width=600, height=600)

# Border
border_pen = turtle.Turtle()
border_pen.color("white")
border_pen.pensize(3)
border_pen.penup()
border_pen.setposition(-290, -290)
border_pen.pendown()
for _ in range(4):
    border_pen.forward(580)
    border_pen.left(90)
border_pen.hideturtle()

# Player
player = turtle.Turtle()
player.shape("turtle")
player.color("green")
player.penup()
player.speed(0)

# Food
food = turtle.Turtle()
food.shape("circle")
food.color("red")
food.penup()
food.speed(0)
food.setposition(random.randint(-280, 280), random.randint(-280, 280))

# Score display
score_display = turtle.Turtle()
score_display.color("white")
score_display.penup()
score_display.hideturtle()
score_display.setposition(-280, 260)

# movement flags
turn_left_pressed = False
turn_right_pressed = False
accel_pressed = False

# Functions
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

def move():
    # Handle turning
    if turn_left_pressed:
        player.left(5)
    if turn_right_pressed:
        player.right(5)
    
    # Handle speed
    speed = 6 if accel_pressed else 4
    player.forward(speed)

    # Check collision with food
    if player.distance(food) < 20:
        global score
        score += 1
        food.setposition(random.randint(-280, 280), random.randint(-280, 280))
        update_score()

    # Check collision with border
    x, y = player.position()
    if x > 280 or x < -280 or y > 280 or y < -280:
        game_over()

def update_score():
    score_display.clear()
    score_display.write(f"Score: {score}  High Score: {high_score}", font=("Arial", 16, "normal"))

def game_over():
    global high_score
    if score > high_score:
        high_score = score
        # Save high score
        data = {"high_score": high_score, "scores": []}
        with open(highscore_file, 'w') as f:
            json.dump(data, f)
    score_display.clear()
    score_display.setposition(0, 0)
    score_display.write(f"Game Over!\nScore: {score}\nHigh Score: {high_score}", align="center", font=("Arial", 24, "normal"))
    turtle.done()

# Keyboard bindings
s.listen()
# arrow keys set/clear flags
s.onkeypress(start_turn_left, "Left")
s.onkeyrelease(stop_turn_left, "Left")
s.onkeypress(start_turn_right, "Right")
s.onkeyrelease(stop_turn_right, "Right")
# Up toggles faster forward motion
s.onkeypress(start_accel, "Up")
s.onkeyrelease(stop_accel, "Up")

# Initial score
score = 0
update_score()

# Main game loop
def main_loop():
    move()
    s.update()
    s.ontimer(main_loop, 16)  # roughly 60 frames per second

main_loop()
s.mainloop()