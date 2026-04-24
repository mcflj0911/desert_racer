# 🌵 Desert Pixel Racer: Definitive Edition

A high-speed, lofi-aesthetic arcade racing game built with Python and Pygame. Navigate the neon desert, manage your heat level, and use power-ups to outmaneuver a persistent police force.

## 🎮 Game Features
* **Dynamic Difficulty System**: Three distinct handling modes (Easy, Normal, Hard) that adjust acceleration and maneuverability.
* **Wanted Level Mechanics**: Pursuits trigger at 150 KMH. Higher speeds result in more units and increased police aggression.
* **Traffic Chaos Physics**: Police units are physical entities. You can tactically bait police into colliding with civilian traffic to disable them.
* **Power-up System**:
    * 🟢 **Slow-Mo**: Significantly reduces game speed temporarily for precise maneuvering.
    * 🔵 **EMP**: Disables all civilian cars and police units on screen for a short duration.
* **Progressive Speed**: The world accelerates logarithmically as your score increases, pushing your reflexes to the limit.
* **Zero Overlap Spawning**: A strict hitbox validation system ensures that obstacles, power-ups, and doodads (cacti/rocks) never spawn on top of each other.

## 🛠️ Controls
* **WASD or Arrow Keys**: Drive and drift your vehicle.
* **Space / Enter**: Confirm menu selections.
* **'R' Key**: Return to the menu after a crash or being busted.

## 🚦 Handling Modes
| Mode | Physics Description |
| :--- | :--- |
| **Easy** | Lower acceleration for better control. |
| **Normal** | Balanced momentum and realistic turning arcs. |
| **Hard** | Exponential acceleration; extremely slippery at high speeds. |

## 🚀 Installation & Running
1.  **Ensure Python is installed** (v3.6+ recommended).
2.  **Install Pygame**:
    ```bash
    pip install pygame
    ```
3.  **Required Assets**: The game looks for the following files in the local directory. If missing, it will use colored vector placeholders:
    * Vehicles: `player_car.png`, `obstacle_car.png`, `police_car.png`
    * Environment: `cactus.png`, `rock.png`
    * UI/Power-ups: `star.png`, `slow_down.png`, `emp.png`
    * Audio: `music.mp3`, `crash.mp3`, `slow.mp3`, `emp.mp3`
4.  **Run the Game**:
    ```bash
    python main.py
    ```

## 📜 Police Intel
* **Wanted Level 0**: Below 150 KMH. Safe zone.
* **Wanted Level 1**: 150 KMH. One patrol unit begins the chase.
* **Wanted Level 2+**: 180+ KMH. Multiple units join for pincer maneuvers.
* **Tactical Tip**: If a police unit hits a civilian car, they both despawn, granting you a temporary window of escape.
