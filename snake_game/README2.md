# Snake Game with Levels

A classic Snake game with 5 levels of increasing difficulty, featuring obstacles.

## Features

- 5 levels with progressively more obstacles
- Increasing game speed per level
- More food to collect in higher levels
- Blue obstacles that end the game if hit
- Level progression upon collecting all food

## How to Run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the game:
   ```
   python main2.py
   ```

## Controls

- Use arrow keys to control the snake.
- Eat all red food to advance to the next level.
- Avoid hitting walls, obstacles, or yourself.

## Levels

- **Level 1**: No obstacles, slow speed, 5 foods
- **Level 2**: Some vertical walls, medium speed, 7 foods
- **Level 3**: More walls, faster speed, 10 foods
- **Level 4**: Complex obstacles, fast speed, 12 foods
- **Level 5**: Maximum obstacles, fastest speed, 15 foods

## Troubleshooting

- If the game doesn't start, ensure Pygame is installed correctly.
- Make sure you have Python 3.x installed.