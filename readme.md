# 🌵 Desert Pixel Racer: Definitive Edition

A high-speed, lofi-aesthetic arcade racing game built with Python and Pygame. Navigate the neon desert, outrun the law, and use high-tech power-ups to survive the heat.

## 🎮 Game Features
* **Dynamic Handling System**: Steering responsiveness scales based on your speed and selected mode (Easy: Static, Normal: Logarithmic, Hard: Exponential).
* **Advanced Police AI**: Strategic pursuit begins at 150 KMH. Units increase at every 30 KMH increment thereafter, capping at a 4-unit squad.
* **Traffic Chaos Physics**: Police units are physical entities. You can tactically bait police into colliding with civilian traffic; a collision will despawn both the patrol unit and the civilian vehicle.
* **Neon Aesthetic**: Features pulsing neon glows for power-ups, police sirens, and disabled vehicles.
* **Double Yellow Road Markers**: High-visibility boundaries defining the playable asphalt.
* **Power-up Arsenal**:
    * 🟢 **Slow-Mo**: Reduces speed for precise navigation through heavy traffic.
    * 🔵 **EMP**: Disables all obstacles and police units with a visible cyan disruption aura.
    * 🟠 **Rockets**: Armed with a 3-rocket payload to physically clear paths and neutralize threats.

## 🛠️ Controls
* **WASD or Arrow Keys**: Drive and maneuver your vehicle.
* **Spacebar**: Fire Rockets (during game) or Confirm Selection (in menu).
* **'R' Key**: Return to the main menu after a crash or being busted.

## 🚦 Handling Modes
| Mode | Steering Physics |
| :--- | :--- |
| **Easy** | Static 0.8 acceleration for maximum stability. |
| **Normal** | Logarithmic scaling; responsiveness increases naturally with speed. |
| **Hard** | Exponential scaling; handling becomes extremely sensitive at high KMH. |

## 🚀 Installation & Running
1.  **Dependencies**: Ensure Python 3.6+ and Pygame are installed (`pip install pygame`).
2.  **Asset Directory**: Place all images and audio in a subfolder named `/doodads`.
3.  **Run the Game**:
    ```bash
    python main.py
    ```

## 📜 Police Intel
* **150 KMH**: Wanted Level 1 (1 unit spawned).
* **180 KMH**: Wanted Level 2 (2 units spawned).
* **210 KMH**: Wanted Level 3 (3 units spawned).
* **240 KMH**: Wanted Level 4 (Full 4-unit squad pursuit).
* **Tactical Tip**: Bait police into civilian cars to clear the pursuit. Picking up an EMP or using a Rocket also provides escape windows.
