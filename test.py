from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Game settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_WIDTH = 40
GRID_HEIGHT = 40
initial_game_speed = 200  # Initial milliseconds between moves
speed_increment = 10      # Decrease in speed by this amount
minimum_game_speed = 50   # Minimum delay in milliseconds

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
barrier_speed = 0.05
barriers_active = False

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
            glColor3f(0.2, 0.3, 0.4) if (x + y) % 2 == 0 else glColor3f(0.3, 0.4, 0.5)
            glVertex3f(x, y, 0)
            glVertex3f(x + 1, y, 0)
            glVertex3f(x + 1, y + 1, 0)
            glVertex3f(x, y + 1, 0)
    glEnd()

def draw_snake():
    for i, (x, y) in enumerate(snake):
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, 0.5)
        if i == 0:
            glColor3f(0.9, 0.7, 0.1)  # Head
            glutSolidSphere(0.5, 16, 16)
        else:
            intensity = 0.9 - (0.3 * i / len(snake))
            glColor3f(intensity * 0.9, intensity * 0.6, intensity * 0.1)
            glutSolidCube(0.85)
        glPopMatrix()

def draw_apple():
    if apple_pos:
        x, y = apple_pos
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, 0.5)
        glColor3f(0.8, 0.1, 0.1)
        glutSolidSphere(0.55, 16, 16)
        glPopMatrix()

def draw_moving_barriers():
    glColor3f(0.6, 0.4, 0.2)
    for base_x, y, direction in barriers:
        for offset in range(barrier_length):
            x = base_x + offset * direction
            if 0 <= int(round(x)) < GRID_WIDTH:
                glPushMatrix()
                glTranslatef((int(round(x)) + 0.5), (int(round(y)) + 0.5), 0.5)
                glutSolidCube(0.85)
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
    y = random.randint(0, GRID_HEIGHT - 1)
    # Start anywhere between 0 and GRID_WIDTH-barrier_length
    x = random.randint(0, GRID_WIDTH - barrier_length)
    barrier_direction = random.choice([-1, 1])
    # If moving left, make sure there’s enough space to the left
    if barrier_direction == -1 and x < barrier_length - 1:
        x = barrier_length - 1
    # If moving right, make sure there’s enough space to the right
    if barrier_direction == 1 and x > GRID_WIDTH - barrier_length:
        x = GRID_WIDTH - barrier_length
    barriers.append((x, y, barrier_direction))

def update_game():
    global snake, direction, apple_pos, score, game_over, last_move_time
    global apple_counter, game_speed, barriers_active

    if barriers_active:
        update_barriers()

    current_time = time.time()
    if current_time - last_move_time < game_speed / 1000.0 or game_over or game_paused:
        return
    last_move_time = current_time
    head_x, head_y = snake[0]
    new_head_x = head_x + direction[0]
    new_head_y = head_y + direction[1]
    new_head = (new_head_x, new_head_y)

    # Check collisions with self or bounds
    if (new_head in snake[:-1] or
        new_head_x < 0 or new_head_x >= GRID_WIDTH or
        new_head_y < 0 or new_head_y >= GRID_HEIGHT):
        game_over = True
        return

    snake.insert(0, new_head)

    # Check barrier collision (snake head with any barrier block)
    if barriers_active:
        for base_x, y, b_direction in barriers:
            for offset in range(barrier_length):
                bx = base_x + offset * b_direction
                if int(round(bx)) == new_head_x and int(round(y)) == new_head_y:
                    game_over = True
                    return

    if new_head == apple_pos:
        score += 1
        apple_counter += 1
        apple_pos = None
        spawn_apple()

        # Increase speed/barriers every 5 apples
        if apple_counter % 5 == 0:
            game_speed = max(game_speed - speed_increment, minimum_game_speed)
            if score >= 5:
                if not barriers_active:
                    barriers_active = True
                add_new_barrier()
    else:
        snake.pop()

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