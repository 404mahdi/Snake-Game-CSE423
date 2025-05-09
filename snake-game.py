from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

# Game settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_WIDTH = 40
GRID_HEIGHT = 40
initial_game_speed = 200  # Initial milliseconds between moves
speed_increment = 10      # Decrease in speed by this amount
minimum_game_speed = 50   # Minimum delay in milliseconds
snake_speed_score = 5    # Score at which speed increases

# Game state
snake = []
direction = (1, 0)
apple_pos = None
score = 0
game_over = False
game_paused = False
last_move_time = 0
apple_counter = 0

# Barriers
barriers = []
barrier_length = 4  # Length of the barrier
barrier_speed = 0.03
max_barriers = 8  # Maximum number of barriers
barriers_active = False
barrier_spawn_score = 5  # Spawn at score>1, you can tweak or randomize it
BARRIER_SPEED_INCREMENT = 0.02  # Speed increment for barriers
MAX_BARRIER_SPEED = 0.2  # Maximum speed for barriers

# Egg power-up state
egg_pos = None  # (x, y)
egg_dir = 1     # 1 for right, -1 for left
egg_disp = 0.0  # Floating-point x-displacement for smooth movement
egg_speed = 0.02  # How much to move per frame (smaller=slower)
egg_active = False  # Is the egg currently on the grid?
egg_duration = 5.0  # Duration of 2x speed, in seconds
egg_timer = 0.0     # How long powerup remains
snake_boosted = False  # Is the snake currently boosted?
egg_spawn_score = 3  # Spawn at score>3, you can tweak or randomize it
last_egg_move_time = 0

# Carrot power-up state
carrot_pos = None         # (x, y)
carrot_active = False     # Is the carrot on the grid
carrot_disp = 0.0         # For optional animation (like bounce)
carrot_spawn_score = 6    # Minimum score to start spawning carrots
last_carrot_move_time = 0

# Super Apple (Big Violet/Pink Apple) state
super_apple_pos = None  # (x, y)
super_apple_active = False
super_apple_spawn_score = 7  # Minimum score to start spawning, tweak as desired
super_apple_spawn_chance = 0.01  # Chance to spawn per tick
super_apple_despawn_time = 10.0  # Seconds to remain if not collected
super_apple_timer = 0.0


# Dustbin power-down state
dustbin_pos = None           # (x, y)
dustbin_active = False       # Is the dustbin present on the grid
dustbin_spawn_score = 5      # Minimum score threshold to spawn dustbin
dustbin_spawn_chance = 0.01  # Chance per game tick to spawn the dustbin when conditions are met
dustbin_timer = 0.0          # How long the slow-down effect remains
dustbin_duration = 10.0      # Duration of slow-down in seconds
snake_slowed = False         # Is the snake currently slowed down
last_dustbin_move_time = 0


# Camera settings
camera_pos = (20, -50, 60)
camera_target = (GRID_WIDTH // 2, GRID_HEIGHT // 2, 0)
camera_up = (0, 0, 1)
zoom_level = 1.5

def reset_game():
    global snake, direction, apple_pos, score, game_over, last_move_time
    global apple_counter, game_speed, barriers, barriers_active
    center_x, center_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
    snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
    direction = (1, 0)
    apple_pos = None
    score = 0
    apple_counter = 0
    game_over = False
    barriers_active = False
    game_speed = initial_game_speed
    barriers = []
    last_move_time = time.time()
    spawn_apple()

def spawn_apple():
    global apple_pos
    valid_positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
                       if (x, y) not in snake and not barrier_at_pos(x, y)]
    apple_pos = random.choice(valid_positions) if valid_positions else None

def barrier_at_pos(x, y):
    for base_x, barrier_y, direction in barriers:
        for offset in range(barrier_length):
            bx = base_x + offset * direction
            if int(round(bx)) == x and int(round(barrier_y)) == y:
                return True
    return False

def draw_grid():
    glBegin(GL_QUADS)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if (x + y) % 2 == 0:
                glColor3f(0.2, 0.3, 0.4)
            else:
                glColor3f(0.3, 0.4, 0.5)
            glVertex3f(x, y, 0)
            glVertex3f(x + 1, y, 0)
            glVertex3f(x + 1, y + 1, 0)
            glVertex3f(x, y + 1, 0)
    glEnd()

    # Aura blue border, consistent and atmospheric
    glLineWidth(4.0)
    glColor3f(0.23, 0.36, 0.58)  # Aura-like, consistent blue
    glBegin(GL_LINE_LOOP)
    glVertex3f(0, 0, 0.01)
    glVertex3f(GRID_WIDTH, 0, 0.01)
    glVertex3f(GRID_WIDTH, GRID_HEIGHT, 0.01)
    glVertex3f(0, GRID_HEIGHT, 0.01)
    glEnd()

def draw_snake():
    for i, (x, y) in enumerate(snake):
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, 0.5)
        if i == 0:
            glColor3f(0.9, 0.7, 0.1)
            glutSolidSphere(0.5, 16, 16)
            glPushMatrix()
            glColor3f(1, 1, 1)
            eye_offset = 0.3
            dx, dy = direction
            ox, oy = -dy, dx
            glTranslatef(eye_offset * ox + 0.2 * dx, eye_offset * oy + 0.2 * dy, 0.3)
            glutSolidSphere(0.15, 8, 8)
            glTranslatef(-2 * eye_offset * ox, -2 * eye_offset * oy, 0)
            glutSolidSphere(0.15, 8, 8)
            glColor3f(0, 0, 0)
            glTranslatef(0.05 * dx, 0.05 * dy, 0.05)
            glutSolidSphere(0.07, 6, 6)
            glTranslatef(-0.1 * dx, -0.1 * dy, 0)
            glutSolidSphere(0.07, 6, 6)
            glPopMatrix()
        else:
            intensity = 0.9 - (0.3 * i / len(snake))
            glColor3f(intensity * 0.9, intensity * 0.6, intensity * 0.1)
            if i % 2 == 0:
                glutSolidCube(0.85)
            else:
                glScalef(0.85, 0.85, 0.85)
                glutSolidCube(1.0)
        glPopMatrix()

def draw_apple():
    if apple_pos:
        x, y = apple_pos
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, 0.5)
        glColor3f(0.8, 0.1, 0.1)
        glutSolidSphere(0.55, 16, 16)
        glPushMatrix()
        glColor3f(1.0, 0.3, 0.3)
        glTranslatef(-0.2, 0.2, 0.2)
        glutSolidSphere(0.12, 8, 8)
        glPopMatrix()
        glPushMatrix()
        glColor3f(0.4, 0.2, 0)
        glTranslatef(0, 0, 0.5)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.25, 8, 1)
        glPopMatrix()
        glPushMatrix()
        glColor3f(0.2, 0.7, 0.2)
        glTranslatef(0.05, 0.05, 0.65)
        glRotatef(45, 0, 0, 1)
        glScalef(0.25, 0.35, 0.05)
        glutSolidCube(1.0)
        glPopMatrix()
        glPopMatrix()
        
        
def draw_super_apple():
    if not super_apple_active or super_apple_pos is None:
        return
    x, y = super_apple_pos
    glPushMatrix()
    glTranslatef(x + 0.5, y + 0.5, 0.5)
    glScalef(1.45, 1.45, 1.16)  # Large and slightly taller

    # -- Apple Body (Red, with a slight "gradient") --
    glColor3f(0.86, 0.13, 0.11)  # Vibrant red
    glutSolidSphere(0.6, 40, 32)

    # -- Glossy highlight (upper left) --
    glPushMatrix()
    glColor4f(1.0, 1.0, 1.0, 0.15)
    glTranslatef(-0.22, 0.22, 0.27)
    glRotatef(11, 1, 0, 0)
    glScalef(0.12, 0.24, 0.10)
    glutSolidSphere(1.0, 16, 10)
    glPopMatrix()

    # -- Darker base shadow (lower right) --
    glPushMatrix()
    glColor4f(0.60, 0.10, 0.10, 0.23)
    glTranslatef(0.19, -0.18, -0.36)
    glScalef(0.24, 0.17, 0.11)
    glutSolidSphere(1.0, 12, 8)
    glPopMatrix()

    # -- Leaf (on top, angled, green) --
    glPushMatrix()
    glColor3f(0.23, 0.72, 0.28)
    glTranslatef(0.22, 0.13, 0.52)
    glRotatef(-33, 0, 0, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(0.14, 0.30, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()

    # -- Stem (chunky brown stem) --
    glPushMatrix()
    glColor3f(0.38, 0.22, 0.09)
    glTranslatef(0.04, 0.00, 0.72)
    glRotatef(80, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 0.05, 0.04, 0.20, 10, 2)
    glPopMatrix()

    glPopMatrix()


def draw_moving_barriers():
    glColor3f(0.69, 0.54, 0.32)
    for base_x, y, direction in barriers:
        for offset in range(barrier_length):
            x = base_x + offset * direction
            if 0 <= int(round(x)) < GRID_WIDTH:
                glPushMatrix()
                glTranslatef((int(round(x)) + 0.5), (int(round(y)) + 0.5), 0.5)
                glutSolidCube(0.85)
                glPopMatrix()
                

def draw_dustbin():
    if not dustbin_active or dustbin_pos is None:
        return
    x, y = dustbin_pos
    glPushMatrix()
    glTranslatef(x + 0.5, y + 0.5, 0.72)  # a bit higher for a bigger bin!

    # (1) Main cylindrical bin: bigger and taller!
    glColor3f(0.88, 0.88, 0.9)  # very light grey
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.5, 0.95, 32, 2)  # bigger radius and height
    glPopMatrix()

    # (2) Bin Lid: bigger, thicker lid
    glColor3f(0.82, 0.82, 0.85)
    glPushMatrix()
    glTranslatef(0, 0, 0.95)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.55, 0.09, 32, 1)  # wider and more visible
    glPopMatrix()

    # (3) Lid knob/handle on top
    glColor3f(0.55, 0.55, 0.60)  # darker gray
    glPushMatrix()
    glTranslatef(0, 0, 1.05)
    glutSolidSphere(0.07, 16, 8)
    glPopMatrix()

    # (4) Handles: small cubes on the sides, near the lid
    glColor3f(0.76, 0.76, 0.80)
    for dx in [-0.41, 0.41]:
        glPushMatrix()
        glTranslatef(dx, 0, 0.95)
        glScalef(0.23, 0.07, 0.13)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()
    

def update_barriers():
    global barriers
    if not barriers_active:
        return
    new_barriers = []
    for base_x, y, direction in barriers:
        new_base_x = base_x + barrier_speed * direction
        # Bounce at grid edges
        if direction == 1 and new_base_x + (barrier_length - 1) >= GRID_WIDTH:
            direction = -1
            new_base_x = GRID_WIDTH - barrier_length
        elif direction == -1 and new_base_x <= 0:
            direction = 1
            new_base_x = 0
        new_barriers.append((new_base_x, y, direction))
    barriers[:] = new_barriers

def add_new_barrier():
    global barriers, barrier_speed
    y = random.randint(0, GRID_HEIGHT - 1)
    x = random.randint(0, GRID_WIDTH - barrier_length)
    barrier_direction = random.choice([-1, 1])
    if barrier_direction == -1 and x < barrier_length - 1:
        x = barrier_length - 1
    if barrier_direction == 1 and x > GRID_WIDTH - barrier_length:
        x = GRID_WIDTH - barrier_length
    if len(barriers) < max_barriers and not barrier_at_pos(x, y):
        barriers.append((x, y, barrier_direction))
        
    barrier_speed = min(barrier_speed + BARRIER_SPEED_INCREMENT, MAX_BARRIER_SPEED)
    
def draw_egg():
    if not egg_active or egg_pos is None:
        return
    x, y = egg_pos
    glPushMatrix()
    glTranslatef(x + 0.5 + egg_disp, y + 0.5, 0.5)
    # 1. Main omelet: a "flattened" white sphere (egg white)
    glColor3f(0.97, 0.97, 0.9)  # Slightly off-white
    glPushMatrix()
    glScalef(1.1, 1.1, 0.35)  # Flatten it
    glutSolidSphere(0.65, 32, 32)
    glPopMatrix()
    # 2. Egg edge/border: slightly larger lower layer
    glColor3f(0.88, 0.88, 0.83)  # Whiter border
    glPushMatrix()
    glScalef(1.21, 1.21, 0.2)
    glutSolidSphere(0.73, 32, 32)
    glPopMatrix()
    # 3. Draw the yolk (center)
    glColor3f(0.98, 0.80, 0.18)  # Rich yellow
    glPushMatrix()
    glTranslatef(0.07, 0.06, 0.14)  # Center offset for natural look
    glScalef(0.51, 0.51, 0.25)
    glutSolidSphere(0.62, 24, 24)
    glPopMatrix()
    # 4. (Optional) Yolk highlight
    glColor3f(1.0, 0.92, 0.55)
    glPushMatrix()
    glTranslatef(0.1, 0.13, 0.22)
    glScalef(0.18, 0.18, 0.1)
    glutSolidSphere(0.7, 16, 16)
    glPopMatrix()
    glPopMatrix()
    
    
def spawn_egg():
    global egg_pos, egg_dir, egg_disp, egg_active, last_egg_move_time
    valid_positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
                       if (x, y) not in snake and (apple_pos is None or (x, y) != apple_pos)
                       and not barrier_at_pos(x, y)]
    if valid_positions:
        egg_pos = random.choice(valid_positions)
        egg_dir = random.choice([-1, 1])
        egg_disp = 0.0
        egg_active = True
        last_egg_move_time = time.time()
    else:
        egg_active = False
        
def update_egg():
    global egg_disp, egg_dir, egg_pos, egg_active, last_egg_move_time

    if not egg_active or egg_pos is None:
        return

    now = time.time()
    if now - last_egg_move_time < 0.016:  # ~60fps
        return

    x, y = egg_pos
    egg_disp += egg_dir * egg_speed

    # Bounce at tile edges (keep within [0,1) displacement)
    if egg_disp > 0.5:
        egg_disp = 0.5
        egg_dir = -1
    elif egg_disp < -0.5:
        egg_disp = -0.5
        egg_dir = 1
    last_egg_move_time = now
    

def draw_carrot():
    if not carrot_active or carrot_pos is None:
        return
    x, y = carrot_pos

    glPushMatrix()
    glTranslatef(x + 0.5, y + 0.5, 0.5 + 0.25 * math.sin(time.time()*2))  # even more bounce

    # Carrot body - bigger and longer!
    glColor3f(1.0, 0.46, 0.1)  # orange
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.38, 1.25, 30, 6)  # <-- Bigger (radius), longer (height), fuller
    glPopMatrix()

    # Carrot leaves - also a bit larger and denser
    glColor3f(0.22, 0.7, 0.15)
    glPushMatrix()
    glTranslatef(0, 0, 0.70)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.18, 0.48, 12, 3)
    glPopMatrix()

    # Optionally, add some short side leaves for a "bushy" effect
    glColor3f(0.15, 0.52, 0.08)
    for angle in [30, -30]:
        glPushMatrix()
        glTranslatef(0, 0, 0.60)
        glRotatef(angle, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(0.08, 0.25, 8, 2)
        glPopMatrix()

    glPopMatrix()
    
    
def spawn_carrot():
    global carrot_pos, carrot_active, carrot_disp, last_carrot_move_time
    valid_positions = [
        (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
        if (x, y) not in snake
        and (apple_pos is None or (x, y) != apple_pos)
        and (egg_pos is None or (x, y) != egg_pos)
        and not barrier_at_pos(x, y)
    ]
    if valid_positions:
        carrot_pos = random.choice(valid_positions)
        carrot_active = True
        carrot_disp = 0.0
        last_carrot_move_time = time.time()
    else:
        carrot_active = False
        
def spawn_super_apple():
    global super_apple_pos, super_apple_active, super_apple_timer
    now = time.time()
    valid_positions = [
        (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
        if (x, y) not in snake
        and (apple_pos is None or (x, y) != apple_pos)
        and (egg_pos is None or (x, y) != egg_pos)
        and (carrot_pos is None or (x, y) != carrot_pos)
        and not barrier_at_pos(x, y)
    ]
    if valid_positions:
        super_apple_pos = random.choice(valid_positions)
        super_apple_active = True
        super_apple_timer = now
        
        
def spawn_dustbin():
    global dustbin_pos, dustbin_active, last_dustbin_move_time
    valid_positions = [
        (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
        if (x, y) not in snake
        and (apple_pos is None or (x, y) != apple_pos)
        and (egg_pos is None or (x, y) != egg_pos)
        and (carrot_pos is None or (x, y) != carrot_pos)
        and (super_apple_pos is None or (x, y) != super_apple_pos)
        and not barrier_at_pos(x, y)
    ]
    if valid_positions:
        dustbin_pos = random.choice(valid_positions)
        dustbin_active = True
        last_dustbin_move_time = time.time()
    else:
        dustbin_active = False
    
    
def update_game():
    global snake, direction, apple_pos, score, game_over, last_move_time
    global apple_counter, game_speed, barriers_active
    global egg_pos, egg_dir, egg_disp, egg_active, egg_timer, snake_boosted
    global last_egg_move_time, egg_speed, egg_duration
    global carrot_pos, carrot_active, carrot_disp, last_carrot_move_time
    global super_apple_pos, super_apple_active, super_apple_timer
    global dustbin_pos, dustbin_active, dustbin_timer, dustbin_duration, snake_slowed

    now = time.time()

    # --- Update barriers ---
    if barriers_active:
        update_barriers()

    # --- Egg animation update ---
    if egg_active and egg_pos is not None:
        if now - last_egg_move_time > 0.016:
            egg_disp += egg_dir * egg_speed
            if egg_disp > 0.5:
                egg_disp = 0.5
                egg_dir = -1
            elif egg_disp < -0.5:
                egg_disp = -0.5
                egg_dir = 1
            last_egg_move_time = now

    # --- Carrot animation update (bobbing) ---
    if carrot_active and carrot_pos is not None:
        carrot_disp = 0.15 * math.sin(now * 2)

    # --- Super Apple timeout logic ---
    if super_apple_active:
        if now - super_apple_timer > super_apple_despawn_time:
            super_apple_active = False
            super_apple_pos = None

    # --- Movement Timer (includes egg and dustbin effect) ---
    effective_speed = game_speed // 2 if snake_boosted else (game_speed * 2 if snake_slowed else game_speed)
    if (
        now - last_move_time < effective_speed / 1000.0
        or game_over
        or game_paused
    ):
        return
    last_move_time = now

    # --- Move Snake Head ---
    head_x, head_y = snake[0]
    new_head_x = head_x + direction[0]
    new_head_y = head_y + direction[1]
    new_head = (new_head_x, new_head_y)

    # --- Collisions with self or perimeter ---
    if (
        new_head in snake[:-1]
        or new_head_x < 0 or new_head_x >= GRID_WIDTH
        or new_head_y < 0 or new_head_y >= GRID_HEIGHT
    ):
        game_over = True
        return

    snake.insert(0, new_head)

    # --- Barrier collision ---
    if barriers_active:
        for base_x, y, b_direction in barriers:
            for offset in range(barrier_length):
                bx = base_x + offset * b_direction
                if int(round(bx)) == new_head_x and int(round(y)) == new_head_y:
                    game_over = True
                    return

    # --- Carrot collection ---
    if carrot_active and carrot_pos is not None:
        cx, cy = carrot_pos
        if new_head_x == cx and new_head_y == cy:
            carrot_active = False
            # Optionally: last_carrot_collected_time = time.time()
            snake[:] = snake[:max(3, len(snake) // 2)]

    # --- Super Apple collection (adds 3 points and grows 3 segments) ---
    if super_apple_active and super_apple_pos and new_head == super_apple_pos:
        score += 3
        apple_counter += 1
        # Grow by 3: append 3 segments at the tail
        if len(snake) > 0:
            tail = snake[-1]
            snake.extend([tail] * 3)
        else:
            snake.extend([new_head] * 3)
        super_apple_active = False
        super_apple_pos = None
        if apple_counter % snake_speed_score == 0:
            game_speed = max(game_speed - speed_increment, minimum_game_speed)
            if score >= barrier_spawn_score:
                if not barriers_active:
                    barriers_active = True
                add_new_barrier()

    # --- Egg pickup logic ---
    if egg_active and egg_pos is not None:
        ex, ey = egg_pos
        egg_center_x = ex + 0.5 + egg_disp
        egg_center_y = ey + 0.5
        snake_center_x = new_head_x + 0.5
        snake_center_y = new_head_y + 0.5
        dist2 = (snake_center_x - egg_center_x) ** 2 + (snake_center_y - egg_center_y) ** 2
        if dist2 < 0.45**2:
            egg_active = False
            snake_boosted = True
            egg_timer = egg_duration

    # --- Dustbin collection (slows snake movement) ---
    if dustbin_active and dustbin_pos is not None:
        dbx, dby = dustbin_pos
        if new_head_x == dbx and new_head_y == dby:
            dustbin_active = False
            snake_slowed = True
            dustbin_timer = dustbin_duration

    # --- Egg boost timer countdown ---
    if snake_boosted:
        egg_timer -= effective_speed / 1000.0
        if egg_timer <= 0:
            snake_boosted = False
            egg_timer = 0.0

    # --- Dustbin slow-down timer countdown ---
    if snake_slowed:
        dustbin_timer -= effective_speed / 1000.0
        if dustbin_timer <= 0:
            snake_slowed = False
            dustbin_timer = 0.0

    # --- Apple collection ---
    if new_head == apple_pos:
        score += 1
        apple_counter += 1
        apple_pos = None
        spawn_apple()

        if apple_counter % snake_speed_score == 0:
            game_speed = max(game_speed - speed_increment, minimum_game_speed)
            if score >= barrier_spawn_score:
                if not barriers_active:
                    barriers_active = True
                add_new_barrier()
    else:
        snake.pop()

    # --- Keep snake minimum length ---
    if len(snake) < 3:
        tail = snake[-1]
        while len(snake) < 3:
            snake.append(tail)

    # --- Super Apple spawn logic (now as function call) ---
    if (not super_apple_active 
        and score >= super_apple_spawn_score 
        and random.random() < super_apple_spawn_chance):
        spawn_super_apple()

    # --- Egg spawn logic ---
    if (not egg_active and score > 3 and random.random() < 0.03):
        spawn_egg()

    # --- Carrot spawn logic ---
    if (not carrot_active and score > carrot_spawn_score and random.random() < 0.01):
        spawn_carrot()

    # --- Dustbin spawn logic ---
    if (not dustbin_active and not snake_slowed 
        and score >= dustbin_spawn_score and random.random() < dustbin_spawn_chance):
        spawn_dustbin()

def keyboardListener(key, x, y):
    global direction, game_over, camera_pos, zoom_level, game_paused
    if key == b'=' or key == b'+':
        zoom_level = min(zoom_level + 0.1, 3.0)
    elif key == b'-' or key == b'_':
        zoom_level = max(zoom_level - 0.1, 0.5)
    if key == b'r' and game_over:
        reset_game()
    elif key == b' ' and not game_over:
        game_paused = not game_paused
    elif game_over or game_paused:
        return
    
    speed = 2
    if key == b'w':
        camera_pos = (camera_pos[0], camera_pos[1] + speed, camera_pos[2])
    elif key == b's':
        camera_pos = (camera_pos[0], camera_pos[1] - speed, camera_pos[2])
    elif key == b'a':
        camera_pos = (camera_pos[0] - speed, camera_pos[1], camera_pos[2])
    elif key == b'd':
        camera_pos = (camera_pos[0] + speed, camera_pos[1], camera_pos[2])

def specialKeyListener(key, x, y):
    global direction
    if game_over:
        return
    if key == GLUT_KEY_UP and direction != (0, -1):
        direction = (0, 1)
    elif key == GLUT_KEY_DOWN and direction != (0, 1):
        direction = (0, -1)
    elif key == GLUT_KEY_LEFT and direction != (1, 0):
        direction = (-1, 0)
    elif key == GLUT_KEY_RIGHT and direction != (-1, 0):
        direction = (1, 0)

def mouseListener(button, state, x, y):
    global game_paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        game_paused = not game_paused

def idle():
    update_game()
    update_egg()
    
    glutPostRedisplay()

def showScreen():
    global game_over, score, game_paused
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()
    draw_grid()
    draw_snake()
    draw_apple()
    draw_super_apple()
    draw_egg()
    draw_carrot()
    draw_dustbin()
    if barriers_active:
        draw_moving_barriers()
    draw_text(10, WINDOW_HEIGHT - 30, f"Score: {score}")
    draw_text(10, WINDOW_HEIGHT - 60, "Use arrow keys to control snake")
    draw_text(10, WINDOW_HEIGHT - 90, "WASD to move camera")
    draw_text(10, WINDOW_HEIGHT - 120, "+/- to zoom in/out")
    draw_text(10, WINDOW_HEIGHT - 150, "Space/Left Click to pause")
    if game_over:
        draw_game_over()
    if game_paused and not game_over:
        draw_pause_screen()
    glutSwapBuffers()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    base_fov = 45
    zoomed_fov = base_fov / zoom_level
    gluPerspective(zoomed_fov, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 200)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = camera_pos
    tx, ty, tz = camera_target
    ux, uy, uz = camera_up
    gluLookAt(x, y, z, tx, ty, tz, ux, uy, uz)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_game_over():
    depth_enabled = glIsEnabled(GL_DEPTH_TEST)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.16, 0.17, 0.22, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()
    draw_text(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(WINDOW_WIDTH // 2 - 105, WINDOW_HEIGHT // 2, 'Press "R" to restart', GLUT_BITMAP_HELVETICA_18)
    draw_text(WINDOW_WIDTH // 2 - 80, WINDOW_HEIGHT // 2 - 30, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    if depth_enabled:
        glEnable(GL_DEPTH_TEST)
    else:
        glDisable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)

def draw_pause_screen():
    depth_enabled = glIsEnabled(GL_DEPTH_TEST)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.13, 0.18, 0.25, 0.67)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()
    draw_text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 30, "PAUSED", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 20, "Press Space or Left Click to resume.", GLUT_BITMAP_HELVETICA_18)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    if depth_enabled:
        glEnable(GL_DEPTH_TEST)
    else:
        glDisable(GL_DEPTH_TEST)
    glDisable(GL_BLEND)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"3D Snake Game")
    glClearColor(0.05, 0.05, 0.15, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()