import turtle
import time

# -----------------------
# Screen Setup
# -----------------------
screen = turtle.Screen()
screen.bgcolor("black")
screen.setup(width=600, height=600)
screen.title("Smooth Analog Clock")
screen.tracer(0)

# -----------------------
# Clock Face
# -----------------------
face = turtle.Turtle()
face.hideturtle()
face.speed(0)
face.color("green")
face.pensize(3)

face.penup()
face.goto(0, -210)
face.pendown()
face.circle(210)

face.penup()
face.goto(0, 0)
face.setheading(90)

# Draw hour marks
for _ in range(12):
    face.forward(190)
    face.pendown()
    face.forward(20)
    face.penup()
    face.goto(0, 0)
    face.right(30)

# -----------------------
# Hands
# -----------------------
hour_hand = turtle.Turtle()
minute_hand = turtle.Turtle()
second_hand = turtle.Turtle()

for hand in (hour_hand, minute_hand, second_hand):
    hand.hideturtle()
    hand.speed(0)
    hand.penup()
    hand.goto(0, 0)
    hand.setheading(90)

hour_hand.color("white")
hour_hand.pensize(6)

minute_hand.color("blue")
minute_hand.pensize(4)

second_hand.color("gold")
second_hand.pensize(2)

# -----------------------
# Update Function
# -----------------------
def update_clock():
    while True:
        h = int(time.strftime("%I"))
        m = int(time.strftime("%M"))
        s = int(time.strftime("%S"))

        # Clear only hands
        hour_hand.clear()
        minute_hand.clear()
        second_hand.clear()

        # Hour hand (smooth movement with minutes)
        hour_angle = (h + m / 60) * 30
        hour_hand.setheading(90 - hour_angle)
        hour_hand.pendown()
        hour_hand.forward(100)
        hour_hand.penup()
        hour_hand.goto(0, 0)

        # Minute hand
        minute_angle = (m + s / 60) * 6
        minute_hand.setheading(90 - minute_angle)
        minute_hand.pendown()
        minute_hand.forward(160)
        minute_hand.penup()
        minute_hand.goto(0, 0)

        # Second hand
        second_angle = s * 6
        second_hand.setheading(90 - second_angle)
        second_hand.pendown()
        second_hand.forward(180)
        second_hand.penup()
        second_hand.goto(0, 0)

        screen.update()
        time.sleep(1)

# -----------------------
# Run Clock
# -----------------------
update_clock()
screen.mainloop()