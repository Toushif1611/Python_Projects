# Water Physics Simulation

A simple Pygame-based simulation of water molecules in a draggable container, demonstrating basic particle physics with gravity, collisions, and flow.

## Features

- **Draggable Box**: Click and drag the white rectangular box to move it around the screen.
- **Water Molecules**: 50 blue particles that simulate water behavior.
- **Gravity**: Molecules fall downward due to simulated gravity.
- **Settling**: Molecules accumulate at the bottom of the box with soft bounces and friction.
- **Collisions**: Particles collide with each other and the box walls, preventing overlap and creating realistic flow.
- **Flow Dynamics**: When the box moves, molecules receive momentum, causing sloshing and flow effects.
- **Boundary Clamping**: Molecules are always contained within the box.

## How to Run

1. Ensure you have Python and Pygame installed:
   ```
   pip install pygame
   ```

2. Run the simulation:
   ```
   python main.py
   ```

3. Interact:
   - Click on the white box and drag to move it.
   - Watch the blue molecules flow and settle.

4. Close the window to exit.

## Code Explanation

### Setup
- **Imports**: `pygame`, `random`, `math` for graphics, randomness, and calculations.
- **Screen**: 800x600 window with black background.
- **Box**: White rectangle (200x100) starting at center, with dragging logic.
- **Molecules**: List of 50 dictionaries with position (`x`, `y`) and velocity (`dx`, `dy`).

### Main Loop
- **Event Handling**:
  - `MOUSEBUTTONDOWN`: Detects if click is on box, starts dragging.
  - `MOUSEMOTION`: Updates box position and applies velocity to molecules for flow.
  - `MOUSEBUTTONUP`: Stops dragging.
  - `QUIT`: Exits the program.

- **Molecule Updates**:
  - **Gravity**: Adds 0.1 to `dy` each frame.
  - **Position Update**: Moves molecules based on velocity.
  - **Clamping**: Ensures molecules stay within box (5px margin).
  - **Bounces**: Reverses velocity on wall hits, with soft bottom bounce and friction.
  - **Randomness**: Adds small random forces for turbulence.
  - **Damping**: Reduces velocity over time for settling.

- **Collisions**:
  - Checks all pairs of molecules.
  - If distance < 8 (2 * radius), separates them and swaps velocities.

- **Drawing**:
  - Fills screen black.
  - Draws white box outline.
  - Draws blue circles for molecules.

- **Update**: Refreshes display at 60 FPS.

### Key Variables
- `box_x, box_y`: Box position.
- `box_dx, box_dy`: Box movement velocity (for flow).
- `molecules`: List of particle dicts.
- `MOL_RADIUS = 4`: Collision and draw radius.

### Physics Notes
- **Gravity**: Constant downward acceleration.
- **Collisions**: Simple elastic exchanges; no advanced physics.
- **Flow**: Box movement imparts velocity to particles, simulating inertia.
- **Settling**: Damping and friction make particles come to rest at bottom.

## Customization
- Change `num_molecules` for more/less particles.
- Adjust gravity (0.1), damping (0.98), or collision force.
- Modify box size or colors.

## Gas Simulation Variant

You can easily modify the code to simulate gas molecules instead of water. Gases behave differently: no gravity, higher speeds, and molecules fill the space randomly without settling.

### Changes for Gas
- **Remove Gravity**: Comment out or remove `mol['dy'] += 0.1`.
- **Increase Speeds**: Set initial `dx` and `dy` to `random.uniform(-3, 3)`.
- **Remove Settling**: Remove soft bounce and friction at the bottom; keep wall bounces.
- **Adjust Randomness**: Increase random forces (e.g., `random.uniform(-0.2, 0.2)`) for more turbulence.
- **Increase Particles**: Set `num_molecules = 100` for denser gas.
- **Color Change**: Change molecule color to green for distinction.

### Gas Features
- **Free Motion**: Molecules bounce off walls and each other, filling the container.
- **High Energy**: Faster, more random movement simulating kinetic theory.
- **No Settling**: Particles don't accumulate at the bottom.
- **Flow**: Box movement still imparts momentum for dynamic effects.

Apply the changes above to `main.py` and run for a gas simulation!</content>
<parameter name="filePath">c:\Users\MacAir\OneDrive\Desktop\GITDEMO\Python_Projects\Water_physics\README.md