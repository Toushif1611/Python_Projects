import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Water Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 18)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
GRAY = (180, 180, 180)

# Box
box_width, box_height = 300, 180
box_x, box_y = WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2
box_dx, box_dy = 0, 0
box_dragging = False
box_offset_x, box_offset_y = 0, 0

# Properties
properties = {
    "particle_count": 100,
    "radius": 4,
    "mass": 1.0,
    "gravity": 0.10,
    "bounce": 0.50,
    "drag": 0.98,
    "jitter": 0.08,
    "flow_force": 0.015,
    "viscosity": 0.08,
    "surface_tension": 0.03
}

selected_property = 0
property_names = list(properties.keys())

# Molecules
num_molecules = properties["particle_count"]
molecules = []

def create_molecule():
    r = int(properties["radius"])
    return {
        'x': random.randint(box_x + 20, box_x + box_width - 20),
        'y': random.randint(box_y + 20, box_y + box_height - 20),
        'dx': random.uniform(-1, 1),
        'dy': random.uniform(-1, 1),
        'mass': properties["mass"],
        'radius': r
    }

for _ in range(num_molecules):
    molecules.append(create_molecule())

def sync_molecule_properties():
    for mol in molecules:
        mol["mass"] = properties["mass"]
        mol["radius"] = int(properties["radius"])

def apply_fluid_forces():
    viscosity = properties["viscosity"]
    surface_tension = properties["surface_tension"]

    for i in range(len(molecules)):
        for j in range(i + 1, len(molecules)):
            mol1 = molecules[i]
            mol2 = molecules[j]

            dx = mol2['x'] - mol1['x']
            dy = mol2['y'] - mol1['y']
            dist = math.hypot(dx, dy)

            interaction_radius = (mol1['radius'] + mol2['radius']) * 2.2
            if dist == 0 or dist > interaction_radius:
                continue

            nx = dx / dist
            ny = dy / dist

            rvx = mol2['dx'] - mol1['dx']
            rvy = mol2['dy'] - mol1['dy']

            rel_vel = rvx * nx + rvy * ny
            visc_force = viscosity * rel_vel

            fx = visc_force * nx
            fy = visc_force * ny

            mol1['dx'] += fx / mol1['mass']
            mol1['dy'] += fy / mol1['mass']
            mol2['dx'] -= fx / mol2['mass']
            mol2['dy'] -= fy / mol2['mass']

            rest_dist = mol1['radius'] + mol2['radius'] + 2
            stretch = dist - rest_dist

            if stretch > 0:
                tension = min(surface_tension * stretch, 0.08)
                fx = tension * nx
                fy = tension * ny

                mol1['dx'] += fx / mol1['mass']
                mol1['dy'] += fy / mol1['mass']
                mol2['dx'] -= fx / mol2['mass']
                mol2['dy'] -= fy / mol2['mass']

def handle_collisions():
    for i in range(len(molecules)):
        for j in range(i + 1, len(molecules)):
            mol1 = molecules[i]
            mol2 = molecules[j]

            dx = mol2['x'] - mol1['x']
            dy = mol2['y'] - mol1['y']
            dist = math.hypot(dx, dy)
            min_dist = mol1['radius'] + mol2['radius']

            if 0 < dist < min_dist:
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist

                mol1['x'] -= nx * overlap / 2
                mol1['y'] -= ny * overlap / 2
                mol2['x'] += nx * overlap / 2
                mol2['y'] += ny * overlap / 2

                rvx = mol2['dx'] - mol1['dx']
                rvy = mol2['dy'] - mol1['dy']
                vel = rvx * nx + rvy * ny

                if vel > 0:
                    continue

                restitution = properties["bounce"]
                impulse = -(1 + restitution) * vel
                impulse /= (1 / mol1["mass"] + 1 / mol2["mass"])

                ix = impulse * nx
                iy = impulse * ny

                mol1['dx'] -= ix / mol1["mass"]
                mol1['dy'] -= iy / mol1["mass"]
                mol2['dx'] += ix / mol2["mass"]
                mol2['dy'] += iy / mol2["mass"]

def clamp_to_box(mol):
    r = mol["radius"]

    if mol['x'] < box_x + r:
        mol['x'] = box_x + r
        mol['dx'] *= -properties["bounce"]

    if mol['x'] > box_x + box_width - r:
        mol['x'] = box_x + box_width - r
        mol['dx'] *= -properties["bounce"]

    if mol['y'] < box_y + r:
        mol['y'] = box_y + r
        mol['dy'] *= -properties["bounce"]

    if mol['y'] > box_y + box_height - r:
        mol['y'] = box_y + box_height - r
        mol['dy'] *= -properties["bounce"]
        mol['dx'] *= 0.95

def draw_box():
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 2)

def draw_ui():
    panel_x, panel_y = 20, 20
    title = font.render("UP/DOWN select | LEFT/RIGHT change | R reset", True, YELLOW)
    screen.blit(title, (panel_x, panel_y))

    for i, name in enumerate(property_names):
        color = YELLOW if i == selected_property else WHITE
        value = properties[name]
        text = f"{name}: {value:.3f}" if isinstance(value, float) else f"{name}: {value}"
        screen.blit(font.render(text, True, color), (panel_x, panel_y + 40 + i * 28))

def adjust_property(name, delta):
    if name == "particle_count":
        new_count = max(10, min(500, properties[name] + delta * 10))
        if new_count != properties[name]:
            properties[name] = new_count
            current_count = len(molecules)
            if new_count > current_count:
                for _ in range(new_count - current_count):
                    molecules.append(create_molecule())
            elif new_count < current_count:
                del molecules[new_count:]
    elif name == "radius":
        properties[name] = max(2, min(12, properties[name] + int(delta)))
    elif name == "mass":
        properties[name] += delta * 0.1
    elif name == "gravity":
        properties[name] += delta * 0.01
    elif name == "bounce":
        properties[name] += delta * 0.05
    elif name == "drag":
        properties[name] += delta * 0.005
    elif name == "jitter":
        properties[name] += delta * 0.01
    elif name == "flow_force":
        properties[name] += delta * 0.002
    elif name == "viscosity":
        properties[name] += delta * 0.01
    elif name == "surface_tension":
        properties[name] += delta * 0.005

    sync_molecule_properties()

def reset_properties():
    properties.update({
        "particle_count": 100,
        "radius": 4,
        "mass": 1.0,
        "gravity": 0.10,
        "bounce": 0.50,
        "drag": 0.98,
        "jitter": 0.08,
        "flow_force": 0.015,
        "viscosity": 0.08,
        "surface_tension": 0.03
    })
    sync_molecule_properties()

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_property = (selected_property - 1) % len(property_names)
            elif event.key == pygame.K_DOWN:
                selected_property = (selected_property + 1) % len(property_names)
            elif event.key == pygame.K_LEFT:
                adjust_property(property_names[selected_property], -1)
            elif event.key == pygame.K_RIGHT:
                adjust_property(property_names[selected_property], 1)
            elif event.key == pygame.K_r:
                reset_properties()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if box_x <= mx <= box_x + box_width and box_y <= my <= box_y + box_height:
                box_dragging = True
                box_offset_x = mx - box_x
                box_offset_y = my - box_y

        elif event.type == pygame.MOUSEBUTTONUP:
            box_dragging = False

        elif event.type == pygame.MOUSEMOTION and box_dragging:
            mx, my = pygame.mouse.get_pos()
            new_x = mx - box_offset_x
            new_y = my - box_offset_y

            box_dx = new_x - box_x
            box_dy = new_y - box_y

            box_x, box_y = new_x, new_y

            for mol in molecules:
                mol['dx'] += box_dx * properties["flow_force"]
                mol['dy'] += box_dy * properties["flow_force"]

    apply_fluid_forces()

    for mol in molecules:
        mol['dy'] += properties["gravity"]
        mol['dx'] += random.uniform(-properties["jitter"], properties["jitter"])
        mol['dy'] += random.uniform(-properties["jitter"] * 0.5, properties["jitter"] * 0.5)
        mol['dx'] *= properties["drag"]
        mol['dy'] *= properties["drag"]

        mol['x'] += mol['dx']
        mol['y'] += mol['dy']

    handle_collisions()

    for mol in molecules:
        clamp_to_box(mol)

    draw_box()

    for mol in molecules:
        pygame.draw.circle(screen, BLUE, (int(mol['x']), int(mol['y'])), mol['radius'])

    draw_ui()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()