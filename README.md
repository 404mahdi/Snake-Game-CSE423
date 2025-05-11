---
# 🐍 3D Snake Game
---

## 📄 Project Information

- **Course**: **CSE423 — Computer Graphics**
- **Semester**: **Spring 2025**
- **Institution**: **Brac University**
- **Submission Date**: **09-05-2025**

---

## Project Overview

Our project is a modern 3D version of the classic Snake game, implemented using Python, OpenGL (PyOpenGL), and GLUT. The game features an interactive 3D environment, advanced camera controls, lively power-ups and obstacles, and polished graphics to create a visually stimulating and engaging experience.

---

## Features

### 👾 Core Gameplay

- **3D Snake Movement:** The snake moves in a 40x40 grid rendered in 3D.
- **Arrow Key Control:** Direct the snake with keyboard arrow keys.
- **Growth & Collision:** Snake grows longer by eating apples. Collision with self, the boundary, or barriers ends the game.
- **Game Over State:** Dedicated overlay with score and restart instructions.
- **Pause Functionality:** Space bar or left mouse click toggles pause; displays a pause overlay.
- **Restart Functionality:** On pressing "R" at game over, the entire game resets with a clean grid.

### 🍏 Food and Scoring

- **Red Apple:** Regular food; increases score and snake length by 1. Respawns after being eaten.
- **Score Display:** Score is always shown; the game increases in speed every 5 apples eaten (configurable).

### 🔮 Power-Ups and Obstacles

- **Moving Barriers:**  
  Spawn after a threshold score, move horizontally, and cause game over on collision. Limited in quantity, with increasing speed as score rises.
- **Super Apple:**  
  Provides +3 score and length, appears temporarily after reaching a certain score.
- **Egg Power-Up (Speed Boost):**  
  Animated, provides temporary 2x speed for the snake.
- **Carrot Power-Up (Shrink):**  
  Animated bounce, halves snake length (minimum remains 3).
- **Dustbin Power-Down (Slow):**  
  Temporarily slows the snake.

### 🎨 Visuals & User Interface

- **OpenGL 3D Rendering:**  
  Distinct models and color for each entity.
- **Score and Controls HUD:**  
  Persistent display of score and basic controls.
- **Decorative Aura Border:**  
  Blue border around the game grid.
- **Pause and Game Over Screens:**  
  Overlays with clear instructions.

### 🖱️ Camera Controls

- **Move Camera:**  
  W/A/S/D, with movement bounds.
- **Zoom:**  
  `+`/`-`, min and max zoom enforced.

---

## 📦 Installation & Running

### **Quick Start: Using OpenGL.zip**

1. **Extract the opengl.zip** file included in this repository.
2. **Navigate to the extracted folder** using a terminal/command prompt.
3. **Run the game:**
   ```sh
   python snake-game.py
   ```

---

## 🧩 How to Play

- **Arrow Keys:** Move the snake
- **W/A/S/D:** Pan the 3D camera (movement is bounded)
- **+/-:** Zoom camera in and out
- **Space or Left Click:** Pause/Unpause game
- **R:** Restart the game after game over
- **Objective:** Eat apples, score high, collect power-ups, avoid obstacles and survive as long as possible!

---

## 📷 Screenshots

![image](https://s4.gifyu.com/images/bsbMs.gif)

![image](https://s4.gifyu.com/images/bsbzo.gif)

![image](https://s4.gifyu.com/images/bsbLM.gif)

![image](https://github.com/user-attachments/assets/54084973-0108-4aae-ae69-208001eafd82)


---
