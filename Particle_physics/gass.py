import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gas Physics Simulation")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 80, 80)
BLUE = (80, 160, 255)
YELLOW = (255, 220, 80)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)

DEFAULT_RADIUS = 4

SIM_WIDTH = 760
PANEL_X = SIM_WIDTH + 10
PANEL_WIDTH = WIDTH - SIM_WIDTH - 20

box_width, box_height = 200, 100
box_x, box_y = SIM_WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2
box_dragging = False
box_offset_x, box_offset_y = 0, 0

num_molecules = 30
mass_scale = 1.0
collision_elasticity = 1.0
wall_elasticity = 1.0
gravity = 0.0
R = 0.05
temperature_scale = 1.0

wall_collisions = 0
last_time = pygame.time.get_ticks()
pressure = 0.0

slider_y = HEIGHT - 50
sliders = {
    'width': {'x': 40, 'y': slider_y, 'width': 100, 'min': 50, 'max': 400, 'value': box_width, 'label': 'Width'},
    'height': {'x': 150, 'y': slider_y, 'width': 100, 'min': 50, 'max': 400, 'value': box_height, 'label': 'Height'},
    'radius': {'x': 260, 'y': slider_y, 'width': 100, 'min': 2, 'max': 10, 'value': DEFAULT_RADIUS, 'label': 'Radius'},
    'num': {'x': 370, 'y': slider_y, 'width': 100, 'min': 10, 'max': 100, 'value': num_molecules, 'label': 'Num'},
    'mass': {'x': 480, 'y': slider_y, 'width': 100, 'min': 0.5, 'max': 5.0, 'value': 1.0, 'label': 'Mass'},
    'elas': {'x': 590, 'y': slider_y, 'width': 100, 'min': 0.5, 'max': 1.0, 'value': 1.0, 'label': 'Elastic'},
    'wall': {'x': 700, 'y': slider_y, 'width': 100, 'min': 0.5, 'max': 1.0, 'value': 1.0, 'label': 'Wall'}
}
dragging_slider = None

process_modes = ["None", "Isothermal", "Isochoric", "Isobaric", "Adiabatic"]
selected_process = "None"

buttons = {}
button_y = 40
button_h = 32
for name in process_modes[1:]:
    buttons[name] = pygame.Rect(PANEL_X, button_y, PANEL_WIDTH, button_h)
    button_y += 42

pv_history = []
max_pv_points = 200

target_temperature = None
target_pressure = None
adiabatic_constant = None
last_volume = box_width * box_height


def update_box():
    global box_x, box_y
    box_x = SIM_WIDTH // 2 - box_width // 2
    box_y = HEIGHT // 2 - box_height // 2


def create_molecule(color=GREEN):
    r = int(sliders['radius']['value'])
    return {
        'x': random.randint(box_x + r, box_x + box_width - r),
        'y': random.randint(box_y + r, box_y + box_height - r),
        'dx': random.uniform(-3, 3),
        'dy': random.uniform(-3, 3),
        'mass': mass_scale,
        'radius': r,
        'color': color
    }


def update_particles():
    global molecules
    current_num = len(molecules)
    if num_molecules > current_num:
        for _ in range(num_molecules - current_num):
            molecules.append(create_molecule())
    elif num_molecules < current_num:
        molecules = molecules[:num_molecules]


molecules = [create_molecule() for _ in range(num_molecules)]


def average_ke():
    total = len(molecules)
    if total == 0:
        return 0.0
    return sum(0.5 * mol['mass'] * (mol['dx'] ** 2 + mol['dy'] ** 2) for mol in molecules) / total


def average_speed():
    total = len(molecules)
    if total == 0:
        return 0.0
    return sum(math.hypot(mol['dx'], mol['dy']) for mol in molecules) / total


def scale_velocities(factor):
    for mol in molecules:
        mol['dx'] *= factor
        mol['dy'] *= factor


def set_process_mode(mode, temperature, volume):
    global selected_process, target_temperature, target_pressure, adiabatic_constant
    selected_process = mode
    if mode == "Isothermal":
        target_temperature = temperature
    elif mode == "Isobaric":
        target_pressure = pressure
    elif mode == "Adiabatic":
        adiabatic_constant = pressure * (volume ** 1.4) if volume > 0 else None


def apply_process_constraints(volume, temperature):
    global pressure

    if selected_process == "Isothermal" and target_temperature is not None and temperature > 0:
        factor = math.sqrt(target_temperature / temperature)
        scale_velocities(factor)

    elif selected_process == "Isobaric" and target_pressure is not None and pressure > 0:
        if volume > 0 and temperature > 0 and len(molecules) > 0:
            desired_temp = (target_pressure * volume) / (len(molecules) * R)
            if desired_temp > 0:
                factor = math.sqrt(desired_temp / temperature)
                scale_velocities(factor)

    elif selected_process == "Adiabatic" and adiabatic_constant is not None and volume > 0 and len(molecules) > 0:
        desired_pressure = adiabatic_constant / (volume ** 1.4)
        desired_temp = (desired_pressure * volume) / (len(molecules) * R)
        if temperature > 0 and desired_temp > 0:
            factor = math.sqrt(desired_temp / temperature)
            scale_velocities(factor)


def handle_collisions():
    for i in range(len(molecules)):
        for j in range(i + 1, len(molecules)):
            m1 = molecules[i]
            m2 = molecules[j]

            dx = m2['x'] - m1['x']
            dy = m2['y'] - m1['y']
            dist = math.hypot(dx, dy)
            min_dist = m1['radius'] + m2['radius']

            if 0 < dist < min_dist:
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist

                m1['x'] -= nx * overlap / 2
                m1['y'] -= ny * overlap / 2
                m2['x'] += nx * overlap / 2
                m2['y'] += ny * overlap / 2

                rvx = m2['dx'] - m1['dx']
                rvy = m2['dy'] - m1['dy']
                vel_along_normal = rvx * nx + rvy * ny

                if vel_along_normal > 0:
                    continue

                e = collision_elasticity
                impulse = -(1 + e) * vel_along_normal
                impulse /= (1 / m1['mass'] + 1 / m2['mass'])

                ix = impulse * nx
                iy = impulse * ny

                m1['dx'] -= ix / m1['mass']
                m1['dy'] -= iy / m1['mass']
                m2['dx'] += ix / m2['mass']
                m2['dy'] += iy / m2['mass']


def draw_sliders():
    font = pygame.font.SysFont(None, 20)
    for slider in sliders.values():
        label = font.render(slider['label'], True, WHITE)
        screen.blit(label, (slider['x'], slider['y'] - 25))
        pygame.draw.rect(screen, WHITE, (slider['x'], slider['y'], slider['width'], 5))
        knob_x = slider['x'] + (slider['value'] - slider['min']) / (slider['max'] - slider['min']) * slider['width']
        pygame.draw.circle(screen, GREEN, (int(knob_x), slider['y'] + 2), 8)

    pygame.draw.rect(screen, RED, (40, HEIGHT - 120, 100, 30))
    pygame.draw.rect(screen, BLUE, (150, HEIGHT - 120, 100, 30))
    screen.blit(font.render("Add Red", True, WHITE), (50, HEIGHT - 112))
    screen.blit(font.render("Add Blue", True, WHITE), (158, HEIGHT - 112))


def draw_info_panel(temperature, theoretical_pressure, n):
    font = pygame.font.SysFont(None, 22)
    volume = box_width * box_height
    avg_spd = average_speed()

    lines = [
        f"Process: {selected_process}",
        f"Particles (n): {n}",
        f"Volume (V): {volume}",
        f"Temperature (T): {temperature:.2f}",
        f"Pressure (P): {pressure:.3f}",
        f"Mass (M): {mass_scale:.2f}",
        f"Elasticity: {collision_elasticity:.2f}",
        f"Wall Elasticity: {wall_elasticity:.2f}",
        f"Gravity: {gravity:.3f}",
        f"Avg speed: {avg_spd:.2f}",
        "H = heat, C = cool"
    ]

    x, y = 10, 10
    for line in lines:
        text = font.render(line, True, WHITE)
        screen.blit(text, (x, y))
        y += 22


def draw_thermo_bars(temperature):
    x = 20
    y = HEIGHT - 180
    width = 20
    scale = 2

    temp_bar = min(100, temperature * scale)
    press_bar = min(100, pressure * 200)
    vol_bar = min(100, (box_width * box_height) / 50)

    pygame.draw.rect(screen, RED, (x, y - temp_bar, width, temp_bar))
    pygame.draw.rect(screen, BLUE, (x + 40, y - press_bar, width, press_bar))
    pygame.draw.rect(screen, GREEN, (x + 80, y - vol_bar, width, vol_bar))

    font = pygame.font.SysFont(None, 18)
    screen.blit(font.render("T", True, WHITE), (x, y + 5))
    screen.blit(font.render("P", True, WHITE), (x + 40, y + 5))
    screen.blit(font.render("V", True, WHITE), (x + 80, y + 5))


def draw_process_buttons():
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 28)

    screen.blit(title_font.render("Iso-processes", True, WHITE), (PANEL_X, 10))

    for name, rect in buttons.items():
        color = YELLOW if selected_process == name else DARK_GRAY
        pygame.draw.rect(screen, color, rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
        text = font.render(name, True, WHITE if selected_process != name else BLACK)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    clear_rect = pygame.Rect(PANEL_X, button_y + 10, PANEL_WIDTH, button_h)
    pygame.draw.rect(screen, GRAY, clear_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, clear_rect, 2, border_radius=6)
    txt = font.render("Clear / None", True, WHITE)
    screen.blit(txt, txt.get_rect(center=clear_rect.center))
    return clear_rect


def draw_pv_plot():
    plot_x = PANEL_X
    plot_y = 300
    plot_w = PANEL_WIDTH
    plot_h = 220
    font = pygame.font.SysFont(None, 22)
    small_font = pygame.font.SysFont(None, 18)

    pygame.draw.rect(screen, DARK_GRAY, (plot_x, plot_y, plot_w, plot_h))
    pygame.draw.rect(screen, WHITE, (plot_x, plot_y, plot_w, plot_h), 2)
    screen.blit(font.render("PV Cycle Plot", True, WHITE), (plot_x + 10, plot_y - 28))

    inner_pad = 30
    gx = plot_x + inner_pad
    gy = plot_y + 10
    gw = plot_w - inner_pad - 10
    gh = plot_h - inner_pad - 20

    pygame.draw.line(screen, WHITE, (gx, gy + gh), (gx + gw, gy + gh), 2)
    pygame.draw.line(screen, WHITE, (gx, gy), (gx, gy + gh), 2)

    screen.blit(small_font.render("V", True, WHITE), (gx + gw - 10, gy + gh + 5))
    screen.blit(small_font.render("P", True, WHITE), (gx - 20, gy - 5))

    if len(pv_history) < 2:
        return

    volumes = [p[0] for p in pv_history]
    pressures = [p[1] for p in pv_history]

    min_v, max_v = min(volumes), max(volumes)
    min_p, max_p = min(pressures), max(pressures)

    if max_v == min_v:
        max_v += 1
    if max_p == min_p:
        max_p += 1

    points = []
    for v, p in pv_history:
        px = gx + (v - min_v) / (max_v - min_v) * gw
        py = gy + gh - (p - min_p) / (max_p - min_p) * gh
        points.append((px, py))

    if len(points) >= 2:
        pygame.draw.lines(screen, GREEN, False, points, 2)

    for pt in points[-5:]:
        pygame.draw.circle(screen, YELLOW, (int(pt[0]), int(pt[1])), 3)

    screen.blit(small_font.render(f"{min_v:.0f}", True, WHITE), (gx, gy + gh + 5))
    screen.blit(small_font.render(f"{max_v:.0f}", True, WHITE), (gx + gw - 35, gy + gh + 5))
    screen.blit(small_font.render(f"{min_p:.2f}", True, WHITE), (gx - 5, gy + gh - 15))
    screen.blit(small_font.render(f"{max_p:.2f}", True, WHITE), (gx - 5, gy))


running = True
while running:
    screen.fill(BLACK)

    clear_button_rect = draw_process_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            if box_x <= mouse_x <= box_x + box_width and box_y <= mouse_y <= box_y + box_height:
                box_dragging = True
                box_offset_x = mouse_x - box_x
                box_offset_y = mouse_y - box_y

            elif 40 <= mouse_x <= 140 and HEIGHT - 120 <= mouse_y <= HEIGHT - 90:
                molecules.append(create_molecule(RED))
                num_molecules = len(molecules)
                sliders['num']['value'] = num_molecules

            elif 150 <= mouse_x <= 250 and HEIGHT - 120 <= mouse_y <= HEIGHT - 90:
                molecules.append(create_molecule(BLUE))
                num_molecules = len(molecules)
                sliders['num']['value'] = num_molecules

            elif clear_button_rect.collidepoint(mouse_x, mouse_y):
                selected_process = "None"
                target_temperature = None
                target_pressure = None
                adiabatic_constant = None

            else:
                clicked_button = False
                for name, rect in buttons.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        current_temp = average_ke()
                        current_vol = box_width * box_height
                        set_process_mode(name, current_temp, current_vol)
                        clicked_button = True
                        break

                if not clicked_button:
                    for key, slider in sliders.items():
                        knob_x = slider['x'] + (slider['value'] - slider['min']) / (slider['max'] - slider['min']) * slider['width']
                        if abs(mouse_x - knob_x) < 10 and abs(mouse_y - slider['y'] - 2) < 10:
                            dragging_slider = key
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            box_dragging = False
            dragging_slider = None

        elif event.type == pygame.MOUSEMOTION:
            if box_dragging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                new_box_x = mouse_x - box_offset_x
                new_box_y = mouse_y - box_offset_y
                delta_x = new_box_x - box_x
                delta_y = new_box_y - box_y

                for mol in molecules:
                    mol['x'] += delta_x
                    mol['y'] += delta_y
                    mol['dx'] += delta_x * 0.01
                    mol['dy'] += delta_y * 0.01

                box_x = new_box_x
                box_y = new_box_y

            elif dragging_slider:
                mouse_x, _ = pygame.mouse.get_pos()
                slider = sliders[dragging_slider]
                rel_x = mouse_x - slider['x']
                ratio = max(0, min(1, rel_x / slider['width']))
                new_value = slider['min'] + ratio * (slider['max'] - slider['min'])

                if dragging_slider == 'width':
                    if selected_process != "Isochoric":
                        box_width = int(new_value)
                        update_box()

                elif dragging_slider == 'height':
                    if selected_process != "Isochoric":
                        box_height = int(new_value)
                        update_box()

                elif dragging_slider == 'radius':
                    new_r = int(new_value)
                    for mol in molecules:
                        mol['radius'] = new_r

                elif dragging_slider == 'num':
                    num_molecules = int(new_value)
                    update_particles()

                elif dragging_slider == 'mass':
                    mass_scale = float(new_value)
                    for mol in molecules:
                        mol['mass'] = mass_scale

                elif dragging_slider == 'elas':
                    collision_elasticity = float(new_value)

                elif dragging_slider == 'wall':
                    wall_elasticity = float(new_value)

                slider['value'] = new_value

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                temperature_scale *= 1.1
            elif event.key == pygame.K_c:
                temperature_scale *= 0.9
            elif event.key == pygame.K_UP:
                gravity += 0.01
            elif event.key == pygame.K_DOWN:
                gravity -= 0.01

    if temperature_scale != 1.0:
        scale_velocities(temperature_scale)
        temperature_scale = 1.0

    for mol in molecules:
        mol['dy'] += gravity
        mol['x'] += mol['dx']
        mol['y'] += mol['dy']

        if mol['x'] <= box_x + mol['radius']:
            wall_collisions += 2 * mol['mass'] * abs(mol['dx'])
            mol['dx'] = abs(mol['dx']) * wall_elasticity
            mol['x'] = box_x + mol['radius']

        elif mol['x'] >= box_x + box_width - mol['radius']:
            wall_collisions += 2 * mol['mass'] * abs(mol['dx'])
            mol['dx'] = -abs(mol['dx']) * wall_elasticity
            mol['x'] = box_x + box_width - mol['radius']

        if mol['y'] <= box_y + mol['radius']:
            wall_collisions += 2 * mol['mass'] * abs(mol['dy'])
            mol['dy'] = abs(mol['dy']) * wall_elasticity
            mol['y'] = box_y + mol['radius']

        elif mol['y'] >= box_y + box_height - mol['radius']:
            wall_collisions += 2 * mol['mass'] * abs(mol['dy'])
            mol['dy'] = -abs(mol['dy']) * wall_elasticity
            mol['y'] = box_y + box_height - mol['radius']

    handle_collisions()

    total = len(molecules)
    temperature = average_ke()
    volume = box_width * box_height

    current_time = pygame.time.get_ticks()
    if current_time - last_time >= 1000:
        perimeter = 2 * (box_width + box_height)
        if perimeter > 0:
            pressure = wall_collisions / perimeter
        wall_collisions = 0
        last_time = current_time

    apply_process_constraints(volume, temperature)
    temperature = average_ke()

    n = total
    theoretical_pressure = (n * R * temperature) / volume if volume > 0 else 0.0

    if len(pv_history) == 0 or abs(volume - last_volume) > 5 or current_time % 200 < 20:
        pv_history.append((volume, theoretical_pressure))
        if len(pv_history) > max_pv_points:
            pv_history.pop(0)

    last_volume = volume

    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 2)

    for mol in molecules:
        pygame.draw.circle(screen, mol['color'], (int(mol['x']), int(mol['y'])), int(mol['radius']))

    pygame.draw.line(screen, GRAY, (SIM_WIDTH, 0), (SIM_WIDTH, HEIGHT), 2)

    draw_sliders()
    draw_info_panel(temperature, theoretical_pressure, n)
    draw_thermo_bars(temperature)
    draw_pv_plot()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()