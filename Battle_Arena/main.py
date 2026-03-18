import pygame
import math
import random
import sys

pygame.init()

# -------------------- SCREEN --------------------
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 35)

# -------------------- COLORS --------------------
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
RED = (255, 60, 60)
GREEN = (0, 255, 0)
GRAY = (120, 120, 120)

# -------------------- SETTINGS --------------------
PLAYER_RADIUS = 15
ENEMY_RADIUS = 15
player_speed = 5
enemy_speed = 5
reload_time = 2000
difficulty_scale = 1

# -------------------- PLAYER --------------------
player_pos = [150, 300]
player_health = 100
player_ammo = 10
player_reloading = False
player_reload_start = 0
player_velocity = [0, 0]  # used for enemy prediction

# -------------------- ENEMY --------------------
enemy_pos = [750, 300]
enemy_health = 100
enemy_ammo = 10
enemy_reloading = False
enemy_reload_start = 0
enemy_state = "attack"
enemy_last_shot = 0
enemy_fire_delay = 400
enemy_strafe_dir = 1

# -------------------- WALLS --------------------
walls = [
    pygame.Rect(420, 150, 120, 40),
    pygame.Rect(420, 410, 120, 40),
    pygame.Rect(200, 200, 40, 200),
    pygame.Rect(660, 200, 40, 200)
]

# -------------------- BULLET --------------------
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, 8, 8)
        self.dx = dx
        self.dy = dy

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)

player_bullets = []
enemy_bullets = []

# -------------------- HELPERS --------------------
def draw_text(text, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))


def intercept_vector(src, tgt, tgt_vel, speed):
    """Return a unit (dx,dy) vector pointing where to fire to intercept target.
    Uses quadratic formula solving |tgt + tgt_vel*t - (src + dir*speed*t)|=0.
    If no solution or target is very slow, returns direct aim.
    """
    tx, ty = tgt
    sx, sy = src
    vx, vy = tgt_vel
    dx = tx - sx
    dy = ty - sy
    a = vx*vx + vy*vy - speed*speed
    b = 2*(dx*vx + dy*vy)
    c = dx*dx + dy*dy
    if abs(a) < 1e-6:
        # linear case
        if abs(b) < 1e-6:
            return 0, 0
        t = -c / b
        if t <= 0:
            return dx/math.hypot(dx,dy), dy/math.hypot(dx,dy)
    else:
        disc = b*b - 4*a*c
        if disc < 0:
            # no intercept possible
            return dx/math.hypot(dx,dy), dy/math.hypot(dx,dy)
        t1 = (-b + math.sqrt(disc)) / (2*a)
        t2 = (-b - math.sqrt(disc)) / (2*a)
        t = min(t for t in (t1,t2) if t>0) if any(t>0 for t in (t1,t2)) else max(t1,t2)
    aim_x = dx + vx*t
    aim_y = dy + vy*t
    mag = math.hypot(aim_x, aim_y)
    if mag == 0:
        return 0,0
    return aim_x/mag, aim_y/mag

def check_wall_collision(rect):
    return any(rect.colliderect(w) for w in walls)

def move_enemy(dx, dy):
    # Move X
    new_rect = pygame.Rect(enemy_pos[0]+dx-ENEMY_RADIUS,
                           enemy_pos[1]-ENEMY_RADIUS,
                           ENEMY_RADIUS*2, ENEMY_RADIUS*2)
    if not check_wall_collision(new_rect):
        enemy_pos[0] += dx

    # Move Y
    new_rect = pygame.Rect(enemy_pos[0]-ENEMY_RADIUS,
                           enemy_pos[1]+dy-ENEMY_RADIUS,
                           ENEMY_RADIUS*2, ENEMY_RADIUS*2)
    if not check_wall_collision(new_rect):
        enemy_pos[1] += dy

    # Clamp to screen
    enemy_pos[0] = max(ENEMY_RADIUS, min(WIDTH-ENEMY_RADIUS, enemy_pos[0]))
    enemy_pos[1] = max(ENEMY_RADIUS, min(HEIGHT-ENEMY_RADIUS, enemy_pos[1]))

def dodge():
    dx = dy = 0
    threats = 0

    # enemy attempts to move perpendicular to incoming bullets
    for b in player_bullets:
        dist = math.hypot(enemy_pos[0]-b.rect.centerx,
                          enemy_pos[1]-b.rect.centery)
        if dist < 200:
            threats += 1
            perp_x = -b.dy
            perp_y = b.dx
            mag = math.hypot(perp_x, perp_y)
            if mag != 0:
                dx += perp_x/mag
                dy += perp_y/mag

    mag = math.hypot(dx, dy)
    if mag != 0:
        dx /= mag
        dy /= mag

    return dx, dy, threats

def draw_health_bar(x, y, health, color):
    pygame.draw.rect(screen, GRAY, (x, y, 200, 20))
    pygame.draw.rect(screen, color, (x, y, 2*health, 20))

# -------------------- GAME LOOP --------------------
running = True

# helper to reset positions and stats (called when a round ends)
def reset_round(win=False):
    global player_pos, player_health, player_ammo, player_reloading, player_reload_start, player_velocity
    global enemy_pos, enemy_health, enemy_ammo, enemy_reloading, enemy_reload_start, enemy_state, enemy_last_shot
    global difficulty_scale, enemy_speed, enemy_fire_delay

    # adjust difficulty when the player wins
    if win:
        difficulty_scale += 0.2
        enemy_speed = 5 * difficulty_scale
        enemy_fire_delay = max(150, int(400 / difficulty_scale))
    else:
        # starting a new game, reset to base values
        difficulty_scale = 1
        enemy_speed = 5
        enemy_fire_delay = 400

    player_pos = [150, 300]
    player_health = 100
    player_ammo = 10
    player_reloading = False
    player_reload_start = 0
    player_velocity = [0, 0]

    enemy_pos = [750, 300]
    enemy_health = 100
    enemy_ammo = 10
    enemy_reloading = False
    enemy_reload_start = 0
    enemy_state = "attack"
    enemy_last_shot = 0
    

    # clear any projectiles from previous round
    player_bullets.clear()
    enemy_bullets.clear()

# initialize (first round)
reset_round()

while running:
    clock.tick(60)
    screen.fill(BLACK)

    # ---------------- EVENTS ----------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player_ammo > 0 and not player_reloading:
                dx = enemy_pos[0] - player_pos[0]
                dy = enemy_pos[1] - player_pos[1]
                angle = math.atan2(dy, dx)
                speed = 8
                player_bullets.append(
                    Bullet(player_pos[0], player_pos[1],
                           math.cos(angle)*speed,
                           math.sin(angle)*speed))
                player_ammo -= 1

            if event.key == pygame.K_r and not player_reloading:
                player_reloading = True
                player_reload_start = pygame.time.get_ticks()

    # ---------------- PLAYER MOVE ----------------
    keys = pygame.key.get_pressed()
    old_x, old_y = player_pos

    new_x, new_y = player_pos[0], player_pos[1]
    if keys[pygame.K_w]: new_y -= player_speed
    if keys[pygame.K_s]: new_y += player_speed
    if keys[pygame.K_a]: new_x -= player_speed
    if keys[pygame.K_d]: new_x += player_speed

    test_rect = pygame.Rect(new_x-PLAYER_RADIUS, player_pos[1]-PLAYER_RADIUS,
                            PLAYER_RADIUS*2, PLAYER_RADIUS*2)
    if not check_wall_collision(test_rect):
        player_pos[0] = new_x

    test_rect = pygame.Rect(player_pos[0]-PLAYER_RADIUS, new_y-PLAYER_RADIUS,
                            PLAYER_RADIUS*2, PLAYER_RADIUS*2)
    if not check_wall_collision(test_rect):
        player_pos[1] = new_y

    player_pos[0] = max(PLAYER_RADIUS, min(WIDTH-PLAYER_RADIUS, player_pos[0]))
    player_pos[1] = max(PLAYER_RADIUS, min(HEIGHT-PLAYER_RADIUS, player_pos[1]))

    player_velocity[0] = (player_pos[0] - old_x) * 60
    player_velocity[1] = (player_pos[1] - old_y) * 60

    # ---------------- ENEMY AI ----------------
    dx = player_pos[0] - enemy_pos[0]
    dy = player_pos[1] - enemy_pos[1]
    dist = math.hypot(dx, dy)

    if dist != 0:
        dx /= dist
        dy /= dist

    dodge_x, dodge_y, threats = dodge()

    SAFE_DISTANCE = 220
    MAX_DISTANCE = 400

    if enemy_ammo == 0 or enemy_health < 30:
        enemy_state = "hide"
    elif enemy_reloading and enemy_health < 50:
        enemy_state = "hide"
    else:
        enemy_state = "attack"

    # ---------------- ATTACK MODE ----------------
    if enemy_state == "attack":

        move_x = 0
        move_y = 0

        # Too far → Chase
        if dist > MAX_DISTANCE:
            move_x = dx * enemy_speed
            move_y = dy * enemy_speed

        # Too close → Move back
        elif dist < SAFE_DISTANCE:
            move_x = -dx * enemy_speed
            move_y = -dy * enemy_speed

        # Ideal range → Strafe (side movement) with occasional direction change
        else:
            perp_x = -dy
            perp_y = dx
            # randomly flip strafing direction every few frames to be less predictable
            if random.random() < 0.02:
                enemy_strafe_dir *= -1

            move_x = perp_x * enemy_speed * enemy_strafe_dir
            move_y = perp_y * enemy_speed * enemy_strafe_dir

        # Apply dodge
        if threats > 0:
            move_x = (move_x + dodge_x * 4) / 2
            move_y = (move_y + dodge_y * 4) / 2

        move_enemy(move_x, move_y)

        # Shoot with lead prediction
        now = pygame.time.get_ticks()
        if dist < MAX_DISTANCE and enemy_ammo > 0 and now - enemy_last_shot > enemy_fire_delay:
            # predict player position using velocity
            tgt_vel = tuple(player_velocity)
            vx, vy = intercept_vector(enemy_pos, player_pos, tgt_vel, 8)
            # if prediction failed, fallback to direct aim
            if vx == 0 and vy == 0:
                angle = math.atan2(player_pos[1] - enemy_pos[1],
                                   player_pos[0] - enemy_pos[0])
                vx = math.cos(angle)
                vy = math.sin(angle)
            speed = 8
            enemy_bullets.append(
                Bullet(enemy_pos[0], enemy_pos[1],
                       vx * speed,
                       vy * speed))
            enemy_ammo -= 1
            enemy_last_shot = now

    # ---------------- HIDE MODE ----------------
    if enemy_state == "hide":
        best_wall = None
        best_dist = float('inf')

        for w in walls:
            wall_dist = math.hypot(w.centerx - enemy_pos[0], w.centery - enemy_pos[1])
            if wall_dist < best_dist:
                best_dist = wall_dist
                best_wall = w

        if best_wall:
            dx = best_wall.centerx - enemy_pos[0]
            dy = best_wall.centery - enemy_pos[1]
            mag = math.hypot(dx, dy)

            if mag != 0:
                dx /= mag
                dy /= mag

            move_enemy(dx * enemy_speed, dy * enemy_speed)

        # reload only if out of ammo
        if enemy_ammo == 0 and not enemy_reloading:
            enemy_reloading = True
            enemy_reload_start = pygame.time.get_ticks()

    # ---------------- RELOAD ----------------
    now = pygame.time.get_ticks()

    if player_reloading and now - player_reload_start > reload_time:
        player_ammo = 10
        player_reloading = False

    if enemy_reloading and now - enemy_reload_start > reload_time:
        enemy_ammo = 10
        enemy_reloading = False

    # ---------------- BULLETS ----------------
    # ---------------- PLAYER BULLETS ----------------
    enemy_rect = pygame.Rect(enemy_pos[0]-ENEMY_RADIUS,
                            enemy_pos[1]-ENEMY_RADIUS,
                            ENEMY_RADIUS*2, ENEMY_RADIUS*2)

    for b in player_bullets[:]:
        b.move()

        hit_enemy = b.rect.colliderect(enemy_rect)
        out_of_bounds = not screen.get_rect().colliderect(b.rect)
        hit_wall = check_wall_collision(b.rect)

        if hit_enemy:
            enemy_health -= 5
            player_bullets.remove(b)
            continue
        elif hit_wall or out_of_bounds:
            player_bullets.remove(b)
            continue

        b.draw()
    # ---------------- ENEMY BULLETS ----------------
    player_rect = pygame.Rect(player_pos[0]-PLAYER_RADIUS,
                            player_pos[1]-PLAYER_RADIUS,
                            PLAYER_RADIUS*2, PLAYER_RADIUS*2)

    for b in enemy_bullets[:]:
        b.move()

        hit_player = b.rect.colliderect(player_rect)
        out_of_bounds = not screen.get_rect().colliderect(b.rect)
        hit_wall = check_wall_collision(b.rect)

        if hit_player:
            player_health -= 5
            enemy_bullets.remove(b)
            continue
        elif hit_wall or out_of_bounds:
            enemy_bullets.remove(b)
            continue

        b.draw()

    # ---------------- DRAW ----------------
    for w in walls:
        pygame.draw.rect(screen, GRAY, w)

    pygame.draw.circle(screen, BLUE, player_pos, PLAYER_RADIUS)
    pygame.draw.circle(screen, RED, enemy_pos, ENEMY_RADIUS)

    draw_text(f"HP: {player_health}", BLUE, 20, 20)
    draw_text(f"Ammo: {player_ammo}", BLUE, 20, 60)
    draw_text(f"Enemy HP: {enemy_health}", RED, 650, 20)

    # ---------------- GAME OVER ----------------
    if enemy_health <= 0:
        draw_text("YOU WIN!", RED, WIDTH//2-100, HEIGHT//2)
        pygame.display.update()
        pygame.time.delay(2000)
        reset_round(win=True)
        continue  # begin next round

    if player_health <= 0:
        draw_text("YOU LOSE!", RED, WIDTH//2-100, HEIGHT//2)
        pygame.display.update()
        pygame.time.delay(2000)
        reset_round(win=False)
        continue

    pygame.display.update()

pygame.quit()
sys.exit()