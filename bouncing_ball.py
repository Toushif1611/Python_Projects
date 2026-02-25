import turtle

# -----------------------
# Screen Setup
# -----------------------
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Smooth Bouncing Ball")
screen.setup(700, 700)
screen.tracer(0)

# -----------------------
# Draw Border
# -----------------------
border = turtle.Turtle()
border.hideturtle()
border.color("green")
border.pensize(5)
border.penup()
border.goto(-320, -320)
border.pendown()

for _ in range(4):
    border.forward(640)
    border.left(90)

# -----------------------
# Ball Setup
# -----------------------
ball = turtle.Turtle()
ball.shape("circle")
ball.color("green")
ball.penup()
ball.goto(0, 200)
ball.speed(0)

ball.dx = 2
ball.dy = 0

gravity = 0.2
bounce_strength = 0.9   # energy loss factor

# -----------------------
# Controls
# -----------------------
def turn_left():
    ball.left(30)

def turn_right():
    ball.right(30)

screen.listen()
screen.onkeypress(turn_left, "Left")
screen.onkeypress(turn_right, "Right")

# -----------------------
# Game Loop (Smooth Version)
# -----------------------
def update():
    # Apply gravity
    ball.dy -= gravity

    # Move ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Wall collision (Left & Right)
    if ball.xcor() > 310 or ball.xcor() < -310:
        ball.dx *= -1

    # Floor collision
    if ball.ycor() < -310:
        ball.sety(-310)
        ball.dy *= -bounce_strength

    # Ceiling collision
    if ball.ycor() > 310:
        ball.sety(310)
        ball.dy *= -1

    screen.update()
    screen.ontimer(update, 16)  # ~60 FPS smooth animation

# Start animation
update()

screen.mainloop()