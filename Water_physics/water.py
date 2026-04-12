import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Water Physics Simulation")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Molecule radius for collision
MOL_RADIUS = 4

# Box setup
box_width, box_height = 200, 100
box_x, box_y = WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2
box_dx, box_dy = 0, 0  # Box velocity
box_dragging = False
box_offset_x, box_offset_y = 0, 0

# Water molecules (particles)
num_molecules = 100
molecules = []
for _ in range(num_molecules):
    mol = {
        'x': random.randint(box_x + 10, box_x + box_width - 10),
        'y': random.randint(box_y + 10, box_y + box_height - 10),
        'dx': random.uniform(-1, 1),
        'dy': random.uniform(-1, 1)
    }
    molecules.append(mol)

# Collision function
def handle_collisions():
    for i in range(len(molecules)):
        for j in range(i + 1, len(molecules)):
            mol1 = molecules[i]
            mol2 = molecules[j]
            dx = mol2['x'] - mol1['x']
            dy = mol2['y'] - mol1['y']
            dist = math.hypot(dx, dy)
            if dist < 2 * MOL_RADIUS and dist > 0:
                # Separate
                overlap = 2 * MOL_RADIUS - dist
                nx = dx / dist
                ny = dy / dist
                mol1['x'] -= nx * overlap / 2
                mol1['y'] -= ny * overlap / 2
                mol2['x'] += nx * overlap / 2
                mol2['y'] += ny * overlap / 2
                # Exchange velocities (simple)
                temp_dx = mol1['dx']
                temp_dy = mol1['dy']
                mol1['dx'] = mol2['dx']
                mol1['dy'] = mol2['dy']
                mol2['dx'] = temp_dx
                mol2['dy'] = temp_dy

# Main loop
running = True
while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if box_x <= mouse_x <= box_x + box_width and box_y <= mouse_y <= box_y + box_height:
                box_dragging = True
                box_offset_x = mouse_x - box_x
                box_offset_y = mouse_y - box_y
        elif event.type == pygame.MOUSEBUTTONUP:
            box_dragging = False
            box_dx, box_dy = 0, 0
        elif event.type == pygame.MOUSEMOTION and box_dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_box_x = mouse_x - box_offset_x
            new_box_y = mouse_y - box_offset_y
            box_dx = new_box_x - box_x
            box_dy = new_box_y - box_y
            box_x = new_box_x
            box_y = new_box_y
            # Apply box velocity to molecules for flow
            for mol in molecules:
                mol['dx'] += box_dx * 0.01  # Increased force for better flow
                mol['dy'] += box_dy * 0.01

    # Update molecules
    for mol in molecules:
        # Add gravity
        mol['dy'] += 0.1
        # Update position with velocity
        mol['x'] += mol['dx']
        mol['y'] += mol['dy']
        # Clamp to box boundaries
        mol['x'] = max(box_x + 5, min(box_x + box_width - 5, mol['x']))
        mol['y'] = max(box_y + 5, min(box_y + box_height - 5, mol['y']))
        # Bounce off sides (now redundant but keep for velocity)
        if mol['x'] <= box_x + 5 or mol['x'] >= box_x + box_width - 5:
            mol['dx'] *= -1
        # Soft bounce off bottom
        if mol['y'] >= box_y + box_height - 5:
            mol['y'] = box_y + box_height - 5
            mol['dy'] *= -0.5  # Soft bounce
            if abs(mol['dy']) < 0.1:
                mol['dy'] = 0
            mol['dx'] *= 0.9  # Friction
        # Bounce off top
        if mol['y'] <= box_y + 5:
            mol['dy'] *= -1
        # Add some randomness for flow
        mol['dx'] += random.uniform(-0.1, 0.1)
        mol['dy'] += random.uniform(-0.05, 0.05)
        # Dampen velocity
        mol['dx'] *= 0.98
        mol['dy'] *= 0.98

    # Handle particle collisions
    handle_collisions()

    # Draw box
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 2)

    # Draw molecules
    for mol in molecules:
        pygame.draw.circle(screen, BLUE, (int(mol['x']), int(mol['y'])), MOL_RADIUS)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
