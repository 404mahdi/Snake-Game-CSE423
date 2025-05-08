from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Game settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
GRID_SIZE = 40
GRID_WIDTH = 40
GRID_HEIGHT = 40
GAME_SPEED = 200  # milliseconds between moves

# Game state
snake = []  # Snake body positions - initialized in reset_game()
direction = (1, 0)  # Initial direction (right)
apple_pos = None
score = 0
game_over = False
last_move_time = 0

# Camera settings
camera_pos = (20, -50, 60)  # Initial camera position
camera_target = (GRID_WIDTH//2, GRID_HEIGHT//2, 0)  # Point camera at center of grid
camera_up = (0, 0, 1)  # Up vector
zoom_level = 1.5  # Added zoom level variable

def reset_game():
    """Reset the game state."""
    global snake, direction, apple_pos, score, game_over, last_move_time
    
    # Initialize snake with size 3
    center_x, center_y = GRID_WIDTH//2, GRID_HEIGHT//2
    snake = [
        (center_x, center_y),      # Head
        (center_x-1, center_y),    # Body
        (center_x-2, center_y)     # Tail
    ]
    
    direction = (1, 0)
    apple_pos = None
    score = 0
    game_over = False
    last_move_time = time.time()
    spawn_apple()

def spawn_apple():
    """Spawn a new apple in a random valid position."""
    global apple_pos
    valid_positions = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if (x, y) not in snake:
                valid_positions.append((x, y))
    
    if valid_positions:
        apple_pos = random.choice(valid_positions)
    else:
        # Player has won by filling the grid
        apple_pos = None

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw text at specified screen coordinates."""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid():
    """Draw the grid floor."""
    # Draw the base grid with a border
    border_size = 0.5
    
    # Draw outer border
    glBegin(GL_QUADS)
    glColor3f(0.35, 0.16, 0.14)  # Dark wood color for border
    # Bottom border
    glVertex3f(-border_size, -border_size, -0.1)
    glVertex3f(GRID_WIDTH + border_size, -border_size, -0.1)
    glVertex3f(GRID_WIDTH + border_size, 0, -0.1)
    glVertex3f(-border_size, 0, -0.1)
    
    # Top border
    glVertex3f(-border_size, GRID_HEIGHT, -0.1)
    glVertex3f(GRID_WIDTH + border_size, GRID_HEIGHT, -0.1)
    glVertex3f(GRID_WIDTH + border_size, GRID_HEIGHT + border_size, -0.1)
    glVertex3f(-border_size, GRID_HEIGHT + border_size, -0.1)
    
    # Left border
    glVertex3f(-border_size, 0, -0.1)
    glVertex3f(0, 0, -0.1)
    glVertex3f(0, GRID_HEIGHT, -0.1)
    glVertex3f(-border_size, GRID_HEIGHT, -0.1)
    
    # Right border
    glVertex3f(GRID_WIDTH, 0, -0.1)
    glVertex3f(GRID_WIDTH + border_size, 0, -0.1)
    glVertex3f(GRID_WIDTH + border_size, GRID_HEIGHT, -0.1)
    glVertex3f(GRID_WIDTH, GRID_HEIGHT, -0.1)
    glEnd()
    
    # Draw base grid - improved color combination
    glBegin(GL_QUADS)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Checkerboard pattern with subtle blue-teal colors
            if (x + y) % 2 == 0:
                glColor3f(0.2, 0.3, 0.4)  # Darker blue-teal
            else:
                glColor3f(0.3, 0.4, 0.5)  # Lighter blue-teal
                
            glVertex3f(x, y, 0)
            glVertex3f(x+1, y, 0)
            glVertex3f(x+1, y+1, 0)
            glVertex3f(x, y+1, 0)
    glEnd()
    
    # Draw subtle grid lines
    glColor3f(0.4, 0.5, 0.6)  # Subtle grid lines
    glBegin(GL_LINES)
    for i in range(GRID_WIDTH + 1):
        glVertex3f(i, 0, 0.01)
        glVertex3f(i, GRID_HEIGHT, 0.01)
    for i in range(GRID_HEIGHT + 1):
        glVertex3f(0, i, 0.01)
        glVertex3f(GRID_WIDTH, i, 0.01)
    glEnd()

def draw_snake():
    """Draw the snake segments."""
    for i, (x, y) in enumerate(snake):
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, 0.5)  # Center of grid cell, slightly above grid
        
        # Head is different color than body
        if i == 0:
            glColor3f(0.9, 0.7, 0.1)  # Gold/yellow head
            glutSolidSphere(0.5, 16, 16)  # Slightly larger head
            
            # Draw eyes
            glPushMatrix()
            glColor3f(1, 1, 1)  # White eyes
            # Left eye
            eye_offset = 0.3
            dx, dy = direction
            # Orthogonal direction for eye placement
            ox, oy = -dy, dx  
            
            # Left eye
            glTranslatef(eye_offset * ox + 0.2 * dx, eye_offset * oy + 0.2 * dy, 0.3)
            glutSolidSphere(0.15, 8, 8)
            
            # Right eye
            glTranslatef(-2 * eye_offset * ox, -2 * eye_offset * oy, 0)
            glutSolidSphere(0.15, 8, 8)
            
            # Eye pupils
            glColor3f(0, 0, 0)  # Black pupils
            glTranslatef(0.05 * dx, 0.05 * dy, 0.05)
            glutSolidSphere(0.07, 6, 6)
            glTranslatef(-0.1 * dx, -0.1 * dy, 0)
            glutSolidSphere(0.07, 6, 6)
            glPopMatrix()
            
        else:
            # Create a gradient effect for the body
            intensity = 0.9 - (0.3 * i / len(snake))
            # Snake body is orange-gold
            glColor3f(intensity * 0.9, intensity * 0.6, intensity * 0.1)
            
            # Alternate between slightly different shapes for visual interest
            if i % 2 == 0:
                glutSolidCube(0.85)
            else:
                glScalef(0.85, 0.85, 0.85)
                glutSolidCube(1.0)
            
        glPopMatrix()

def draw_apple():
    """Draw the apple."""
    if apple_pos:
        x, y = apple_pos
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, 0.5)  # Center of grid cell, slightly above grid
        
        # Apple body (red sphere)
        glColor3f(0.8, 0.1, 0.1)  # Deep red
        glutSolidSphere(0.5, 16, 16)  # Increased size from 0.4 to 0.5
        
        # Apple highlight
        glPushMatrix()
        glColor3f(1.0, 0.3, 0.3)  # Lighter red for highlight
        glTranslatef(-0.2, 0.2, 0.2)  # Adjusted position for larger apple
        glutSolidSphere(0.12, 8, 8)  # Slightly larger highlight
        glPopMatrix()
        
        # Apple stem
        glPushMatrix()
        glColor3f(0.4, 0.2, 0)  # Brown
        glTranslatef(0, 0, 0.45)  # Raised position for larger apple
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.05, 0.05, 0.25, 8, 1)  # Slightly longer stem
        glPopMatrix()
        
        # Leaf
        glPushMatrix()
        glColor3f(0.2, 0.7, 0.2)  # Green
        glTranslatef(0.05, 0.05, 0.6)  # Raised position for larger apple
        glRotatef(45, 0, 0, 1)
        glScalef(0.25, 0.35, 0.05)  # Slightly larger leaf
        glutSolidCube(1.0)
        glPopMatrix()
        
        glPopMatrix()

def draw_game_over():
    """Draw game over screen."""
    # Semi-transparent overlay
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Semi-transparent black overlay
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0, 0, 0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WINDOW_WIDTH, 0)
    glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
    glVertex2f(0, WINDOW_HEIGHT)
    glEnd()
    glDisable(GL_BLEND)
    
    # Game over text
    draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 + 30, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(WINDOW_WIDTH//2 - 80, WINDOW_HEIGHT//2 - 10, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
    draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def setupCamera():
    """Configure the camera's projection and view settings."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    # Apply zoom level to field of view - smaller angle = more zoom
    base_fov = 45
    zoomed_fov = base_fov / zoom_level
    
    gluPerspective(zoomed_fov, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 200)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Position the camera and set its orientation
    x, y, z = camera_pos
    tx, ty, tz = camera_target
    ux, uy, uz = camera_up
    gluLookAt(x, y, z,  # Camera position
              tx, ty, tz,  # Look-at target
              ux, uy, uz)  # Up vector

def update_game():
    """Update the game state."""
    global snake, direction, apple_pos, score, game_over, last_move_time
    
    current_time = time.time()
    if current_time - last_move_time < GAME_SPEED / 1000.0 or game_over:
        return
    
    last_move_time = current_time
    
    # Get the head position
    head_x, head_y = snake[0]
    
    # Calculate new head position
    new_head_x = head_x + direction[0]
    new_head_y = head_y + direction[1]
    new_head = (new_head_x, new_head_y)
    
    # Check for collision with walls
    if (new_head_x < 0 or new_head_x >= GRID_WIDTH or
        new_head_y < 0 or new_head_y >= GRID_HEIGHT):
        game_over = True
        return
    
    # Check for collision with self (excluding the tail if we're not growing)
    if new_head in snake[:-1]:
        game_over = True
        return
    
    # Move the snake
    snake.insert(0, new_head)
    
    # Check if we've eaten an apple
    if new_head == apple_pos:
        score += 1
        # Make sure we spawn a new apple
        apple_pos = None
        spawn_apple()
    else:
        # Remove the tail if we haven't eaten an apple
        snake.pop()

def keyboardListener(key, x, y):
    """Handle keyboard inputs for game control."""
    global direction, game_over, camera_pos, zoom_level
    
    # Zoom controls with +/- keys (= is the unshifted + on most keyboards)
    if key == b'=' or key == b'+':  # Zoom in
        zoom_level = min(zoom_level + 0.1, 3.0)  # Limit max zoom
    elif key == b'-' or key == b'_':  # Zoom out
        zoom_level = max(zoom_level - 0.1, 0.5)  # Limit min zoom
    
    if key == b'r':  # Reset game when R is pressed
        reset_game()
        return
        
    if game_over:
        return
        
    # WASD for camera control
    speed = 2  # Camera movement speed
    if key == b'w':
        camera_pos = (camera_pos[0], camera_pos[1] + speed, camera_pos[2])
    elif key == b's':
        camera_pos = (camera_pos[0], camera_pos[1] - speed, camera_pos[2])
    elif key == b'a':
        camera_pos = (camera_pos[0] - speed, camera_pos[1], camera_pos[2])
    elif key == b'd':
        camera_pos = (camera_pos[0] + speed, camera_pos[1], camera_pos[2])
    elif key == b'q':  # Add up/down controls
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] - speed)
    elif key == b'e':
        camera_pos = (camera_pos[0], camera_pos[1], camera_pos[2] + speed)
        
    # IJKL as alternative directional controls
    elif key == b'i' and direction != (0, -1):  # Up
        direction = (0, 1)
    elif key == b'k' and direction != (0, 1):   # Down
        direction = (0, -1)
    elif key == b'j' and direction != (1, 0):   # Left
        direction = (-1, 0)
    elif key == b'l' and direction != (-1, 0):  # Right
        direction = (1, 0)

def specialKeyListener(key, x, y):
    """Handle special key inputs for snake direction."""
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
    """Handle mouse inputs."""
    pass  # No mouse functionality needed for this game

def idle():
    """Update game state and trigger screen redraw."""
    update_game()
    glutPostRedisplay()

def showScreen():
    """Display function to render the game scene."""
    # Clear color and depth buffers
    if game_over:
        glClearColor(0.2, 0.0, 0.0, 1.0)  # Dark red background for game over
    else:
        glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark navy blue for normal gameplay

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Set up camera
    setupCamera()

    # Always draw the grid, even when the game is over
    draw_grid()

    # Draw scene elements
    if not game_over:
        draw_snake()
        draw_apple()

    # Draw score and instructions
    draw_text(10, WINDOW_HEIGHT - 30, f"Score: {score}")
    draw_text(10, WINDOW_HEIGHT - 60, "Use arrow keys or IJKL to control snake")
    draw_text(10, WINDOW_HEIGHT - 90, "WASD to move camera, Q/E for up/down")
    draw_text(10, WINDOW_HEIGHT - 120, "+/- to zoom in/out")

    # Show game over screen if game is over
    if game_over:
        draw_game_over()

    # Swap buffers for smooth rendering
    glutSwapBuffers()

def main():
    """Initialize OpenGL and start the game."""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"3D Snake Game")
    
    # Set background color (dark navy blue)
    glClearColor(0.05, 0.05, 0.15, 1.0)
    
    # Enable depth testing and blending
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Register callbacks
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Initialize game
    reset_game()
    
    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    main()