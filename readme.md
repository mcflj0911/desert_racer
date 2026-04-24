# 🌵 Desert Pixel Racer: Definitive Edition

A high-speed, lofi-aesthetic arcade racing game built with Python and Pygame. Navigate the neon desert, outrun the law, and use high-tech power-ups to survive the heat.

## 🎮 Game Features
* **Widescreen Experience**: Optimized for an expansive **1400x800** resolution, providing a broader view of the neon wasteland.
* **5-Lane Tactical Highway**: The road has been expanded from 4 to **5 distinct lanes**, allowing for more complex maneuvers and traffic patterns.
* **Environmental Hazards**: 
    * 🌪️ **Wind Gusts**: Semi-transparent wind streaks drift across the screen, adding to the high-speed atmosphere.
    * 🛢️ **Oil Spills**: Glowing, pulsing orange hazards that cause vehicles to lose control upon contact.
* **Dynamic Handling System**: Steering responsiveness scales based on your speed and selected mode (Easy: Static, Normal: Logarithmic, Hard: Exponential).
* **Advanced Police AI**: Strategic pursuit begins at 150 KMH. Units increase at every 30 KMH increment thereafter, capping at a 4-unit squad.
* **Visual Fidelity**: Features dynamic car headlights, pulsing neon glows for power-ups, and a full-screen cyan flash when the EMP is activated.

## 🛠️ Controls
* **WASD or Arrow Keys**: Drive and maneuver your vehicle.
* **Spacebar**: Fire Rockets (during game) or Confirm Selection (in menu).
* **'R' Key**: Return to the main menu after a crash or being busted.

## 🚦 Handling & Difficulty Modes
| Mode | Steering Physics | Spawn Rates |
| :--- | :--- | :--- |
| **Easy** | Static 0.8 acceleration for maximum stability. | High object spacing (1000/2500). |
| **Normal** | Logarithmic scaling; responsiveness increases with speed. | Standard spacing (700/3500). |
| **Hard** | Exponential scaling; handling becomes sensitive at high KMH. | Dense hazards (400/5000). |

## 🚀 Power-up Arsenal
* 🟢 **Slow-Mo**: Reduces game speed for precise navigation through heavy traffic.
* 🔵 **EMP**: Disables all obstacles and police units with a visible cyan disruption aura and full-screen flash.
* 🟠 **Rockets**: Armed with a 3-rocket payload to physically clear paths and neutralize threats.

## 📜 Police Intel
* **150 KMH**: Wanted Level 1 (1 unit spawned).
* **180 KMH**: Wanted Level 2 (2 units spawned).
* **210 KMH**: Wanted Level 3 (3 units spawned).
* **240 KMH**: Wanted Level 4 (Full 4-unit squad pursuit).
* **Tactical Tip**: Police units are physical entities. You can bait them into colliding with civilian traffic to despawn both units.

## 🛠️ Installation & Running
1.  **Dependencies**: Ensure Python 3.6+ and Pygame are installed (`pip install pygame`).
2.  **Asset Directory**: Place all images and audio in a subfolder named `/doodads`.
3.  **Run the Game**:
    ```bash
    python main.py
    ```
