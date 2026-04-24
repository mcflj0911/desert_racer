import pygame
import random
import sys
import os
import math

# --- 1. Initialization ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# UPDATED: Path specifically pointing to the 'doodads' folder
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doodads")

# --- 2. Constants ---
WIDTH, HEIGHT = 800, 600
CAR_SIZE = 60
BASE_GAME_SPEED = 6.0     
SPAWN_RATE = 1000  
POWERUP_SPAWN_RATE = 5000 
LANE_TOP, LANE_BOTTOM = 180, 520
LANES = [210, 330, 450] 

# Colors
NIGHT_BLUE = (15, 10, 25); ASPHALT = (10, 10, 15)         
NEON_PINK = (255, 20, 147); NEON_CYAN = (0, 255, 255)      
NEON_PURPLE = (150, 0, 255); WHITE = (240, 240, 255)
OVERLAY_COLOR = (5, 5, 15, 235); POLICE_RED = (255, 0, 50); POLICE_BLUE = (0, 50, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desert Pixel Racer")
clock = pygame.time.Clock()

# --- 3. Asset Loading ---
def get_image(name, size, fallback_color):
    # This now looks inside /doodads/name
    full_path = os.path.join(BASE_PATH, name)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        except: pass
    # Fallback if image is missing from /doodads
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, fallback_color, (0, 0, size, size), border_radius=10)
    pygame.draw.rect(surf, WHITE, (0, 0, size, size), 2, border_radius=10)
    return surf

player_img = get_image("player_car.png", CAR_SIZE, NEON_PINK)
enemy_img = get_image("obstacle_car.png", CAR_SIZE, NEON_PURPLE)
police_img = get_image("police_car.png", CAR_SIZE, (45, 45, 60))
cactus_img = get_image("cactus.png", 50, (30, 120, 30))
rock_img = get_image("rock.png", 40, (140, 110, 90))
star_img = get_image("star.png", 32, (255, 255, 0))
slow_img = get_image("slow_down.png", 40, (0, 255, 100))
emp_img = get_image("emp.png", 40, NEON_CYAN)

def load_sfx(name):
    # This now looks inside /doodads/name
    path = os.path.join(BASE_PATH, name)
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

crash_sfx = load_sfx("crash.mp3"); slow_sfx = load_sfx("slow.mp3"); emp_sfx = load_sfx("emp.mp3")

# Music loading from /doodads
music_path = os.path.join(BASE_PATH, "music.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.4); pygame.mixer.music.play(-1)

# --- 4. Scenery Classes ---
class Building:
    def __init__(self, x):
        self.width = random.randint(70, 130); self.height = random.randint(180, 400)
        self.x = x; self.y = LANE_TOP - self.height; self.color = (30, 25, 45)
        self.windows = [(random.randint(5, self.width-12), random.randint(10, self.height-20)) for _ in range(10)]
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.width, self.height))
        for wx, wy in self.windows:
            w_col = (255, 255, 180) if random.random() > 0.1 else (20, 20, 40)
            pygame.draw.rect(surf, w_col, (self.x + wx, self.y + wy, 6, 8))

class Doodad:
    def __init__(self, x, img):
        self.img = img; side = random.choice(["top", "bottom"])
        self.y = random.randint(5, LANE_TOP - 55) if side == "top" else random.randint(LANE_BOTTOM + 15, HEIGHT - 50)
        self.x = x; self.rect = pygame.Rect(self.x, self.y, img.get_width(), img.get_height())
    def draw(self, surf): surf.blit(self.img, (self.x, self.y))

# --- 5. Spawn Validation ---
def is_space_clear(new_rect, current_state, min_dist=120):
    for obs in current_state["obstacles"]:
        if new_rect.colliderect(obs["rect"].inflate(min_dist, 20)): return False
    for p in current_state["powerups"]:
        if new_rect.colliderect(p["rect"].inflate(min_dist, 20)): return False
    for d in current_state["doodads"]:
        if new_rect.colliderect(d.rect.inflate(50, 50)): return False
    return True

# --- 6. Game State ---
def reset_game(diff="NORMAL"):
    return {
        "active": True, "difficulty": diff, "score": 0,
        "current_speed": BASE_GAME_SPEED, "speed_modifier": 1.0, 
        "kmh": 0, "max_kmh": 0, "fail_reason": "",
        "player_rect": pygame.Rect(150, 330, CAR_SIZE, CAR_SIZE),
        "vel_x": 0, "vel_y": 0, "obstacles": [], "powerups": [], "scenery": [], "doodads": [],
        "police_a": {"rect": pygame.Rect(-160, LANES[0], CAR_SIZE, CAR_SIZE), "emp": False},
        "police_b": {"rect": pygame.Rect(-160, LANES[2], CAR_SIZE, CAR_SIZE), "emp": False},
        "wanted_level": 0, "emp_timer": 0
    }

state = reset_game()
game_mode = "MENU"
menu_selection = 1
last_key_time = 0
city_lights = [[random.randint(0, WIDTH), random.randint(0, LANE_TOP)] for _ in range(40)]

def draw_info_box():
    box_rect = pygame.Rect(WIDTH - 340, 310, 310, 265)
    info_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA); info_surf.fill((0, 0, 0, 180))
    pygame.draw.rect(info_surf, NEON_CYAN, (0, 0, box_rect.width, box_rect.height), 2, border_radius=8)
    screen.blit(info_surf, box_rect)
    f_s = pygame.font.SysFont("monospace", 14, bold=True); h = pygame.font.SysFont("monospace", 16, bold=True)
    y = 325
    screen.blit(h.render("SYSTEM CONTROLS", True, NEON_CYAN), (WIDTH-325, y))
    screen.blit(f_s.render("> WASD / ARROWS : DRIFT", True, WHITE), (WIDTH-325, y+22))
    screen.blit(f_s.render("> SPACE : CONFIRM SELECT", True, WHITE), (WIDTH-325, y+40))
    screen.blit(f_s.render("> R : RESTART ON CRASH", True, WHITE), (WIDTH-325, y+58))
    screen.blit(h.render("POWERUPS", True, NEON_CYAN), (WIDTH-325, y+90))
    screen.blit(f_s.render("> GREEN: SLOW-MO SPEED", True, (0, 255, 100)), (WIDTH-325, y+112))
    screen.blit(f_s.render("> CYAN : EMP DISRUPTION", True, NEON_CYAN), (WIDTH-325, y+130))
    screen.blit(h.render("POLICE INTEL", True, NEON_CYAN), (WIDTH-325, y+162))
    screen.blit(f_s.render("> 150 KMH: HEAT STARTS", True, NEON_PINK), (WIDTH-325, y+184))
    screen.blit(f_s.render("> SCORE HIGH TO SURVIVE", True, WHITE), (WIDTH-325, y+202))

# --- 7. Main Loop ---
while True:
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if game_mode == "GAME" and not state["active"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: game_mode = "MENU"

    if game_mode == "MENU":
        screen.fill(NIGHT_BLUE)
        
        # Draw Neon Sun
        sun_center = (WIDTH // 2, 210)
        pygame.draw.circle(screen, NEON_PINK, sun_center, 110)
        for i in range(6): 
            pygame.draw.rect(screen, NIGHT_BLUE, (WIDTH//2-110, 210 + (i*20), 220, 4+i))
        
        # --- TITLE TEXT ---
        title_font = pygame.font.SysFont("monospace", 42, bold=True)
        title_text = "DESERT PIXEL RACER"
        shadow = title_font.render(title_text, True, (20, 0, 40))
        screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 4, sun_center[1] - 20 + 4))
        title_surf = title_font.render(title_text, True, WHITE)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, sun_center[1] - 20))
        
        keys = pygame.key.get_pressed()
        if now - last_key_time > 150:
            if keys[pygame.K_w] or keys[pygame.K_UP]: menu_selection = (menu_selection-1)%3; last_key_time = now
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: menu_selection = (menu_selection+1)%3; last_key_time = now
        
        buttons = [("EASY", 360, NEON_CYAN), ("NORMAL", 420, NEON_PURPLE), ("HARD", 480, NEON_PINK)]
        for i, (txt, y_btn, col) in enumerate(buttons):
            is_sel = (menu_selection == i); r = pygame.Rect(40, y_btn, 180, 45)
            pygame.draw.rect(screen, col if is_sel else (30,30,50), r, border_radius=5)
            if is_sel: pygame.draw.rect(screen, WHITE, r, 2, border_radius=5)
            btn_t = pygame.font.SysFont("monospace", 24, True).render(txt, True, WHITE)
            screen.blit(btn_t, (r.centerx-btn_t.get_width()//2, r.centery-btn_t.get_height()//2))
            if is_sel and (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]): state = reset_game(txt); game_mode = "GAME"
        draw_info_box()

    elif game_mode == "GAME":
        if state["active"]:
            if state["emp_timer"] > 0: state["emp_timer"] -= 1.5
            base = BASE_GAME_SPEED + (1.9 * math.log(state["score"] + 1))
            if state["speed_modifier"] < 1.0: state["speed_modifier"] += 0.003
            state["current_speed"] = base * state["speed_modifier"]
            state["kmh"] = state["current_speed"] * 15
            if state["kmh"] > state["max_kmh"]: state["max_kmh"] = state["kmh"]

            keys = pygame.key.get_pressed()
            accel = 1.0 if state["difficulty"] == "NORMAL" else (1.2 if state["difficulty"] == "HARD" else 0.8)
            if keys[pygame.K_w] or keys[pygame.K_UP]: state["vel_y"] -= accel
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: state["vel_y"] += accel
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: state["vel_x"] -= accel
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: state["vel_x"] += accel
            state["vel_x"] *= 0.88; state["vel_y"] *= 0.88
            state["player_rect"].x += state["vel_x"]; state["player_rect"].y += state["vel_y"]
            state["player_rect"].y = max(LANE_TOP, min(state["player_rect"].y, LANE_BOTTOM - CAR_SIZE))
            state["player_rect"].x = max(0, min(state["player_rect"].x, WIDTH - CAR_SIZE))
            state["wanted_level"] = int((state["kmh"] - 150) // 30) + 1 if state["kmh"] >= 150 else 0
            
            for pk in ["police_a", "police_b"]:
                p = state[pk]
                if state["wanted_level"] >= (1 if pk == "police_a" else 2) and not p["emp"]:
                    p["rect"].y += (state["player_rect"].y - p["rect"].y) * 0.04
                    p["rect"].x += 1.8 if (state["player_rect"].x - p["rect"].x) > 130 else 0.5
                    
                    if p["rect"].colliderect(state["player_rect"]): 
                        state["active"] = False; state["fail_reason"] = "BUSTED"
                        if crash_sfx: crash_sfx.play()
                    
                    for obs in state["obstacles"][:]:
                        if p["rect"].colliderect(obs["rect"]):
                            if crash_sfx: crash_sfx.play()
                            state["obstacles"].remove(obs)
                            p["rect"].x = -160
                            break
                else:
                    p["rect"].x -= 10
                    if p["rect"].right < -50: p["rect"].x = -160; p["emp"] = False

            if 'last_s' not in locals() or now - last_s > SPAWN_RATE:
                new_obs_rect = pygame.Rect(WIDTH + 50, random.choice(LANES), CAR_SIZE, CAR_SIZE)
                if is_space_clear(new_obs_rect, state, min_dist=250):
                    state["obstacles"].append({"rect": new_obs_rect, "emp": False})
                    last_s = now
                    if random.random() > 0.6: state["scenery"].append(Building(WIDTH + 100))
                    if random.random() > 0.4:
                        new_d = Doodad(WIDTH + 50, random.choice([cactus_img, rock_img]))
                        if is_space_clear(new_d.rect, state, min_dist=60): state["doodads"].append(new_d)

            if 'last_p' not in locals() or now - last_p > POWERUP_SPAWN_RATE:
                new_p_rect = pygame.Rect(WIDTH + 50, random.choice(LANES) + 10, 40, 40)
                if is_space_clear(new_p_rect, state, min_dist=150):
                    state["powerups"].append({"rect": new_p_rect, "type": random.choice(["SLOW", "EMP"])})
                    last_p = now

            for obs in state["obstacles"][:]:
                obs["rect"].x -= state["current_speed"]
                if not obs["emp"] and state["player_rect"].colliderect(obs["rect"]): 
                    state["active"] = False; state["fail_reason"] = "CRASHED"
                    if crash_sfx: crash_sfx.play()
                if obs["rect"].right < 0: state["obstacles"].remove(obs); state["score"] += 1

            for p_up in state["powerups"][:]:
                p_up["rect"].x -= state["current_speed"]
                if state["player_rect"].colliderect(p_up["rect"]):
                    if p_up["type"] == "SLOW": 
                        state["speed_modifier"] = 0.25; (slow_sfx.play() if slow_sfx else None)
                    else: 
                        state["emp_timer"] = 70; (emp_sfx.play() if emp_sfx else None)
                        for o in state["obstacles"]: o["emp"] = True
                        state["police_a"]["emp"] = state["police_b"]["emp"] = True
                    state["powerups"].remove(p_up)
                elif p_up["rect"].right < 0: state["powerups"].remove(p_up)

            for lit in city_lights: 
                lit[0] -= state["current_speed"] * 0.2
                if lit[0] < 0: lit[0] = WIDTH
            for b in state["scenery"]: b.x -= state["current_speed"] * 0.6
            for d in state["doodads"]: d.x -= state["current_speed"] * 0.8; d.rect.x = d.x
            state["scenery"] = [b for b in state["scenery"] if b.x + b.width > -50]
            state["doodads"] = [d for d in state["doodads"] if d.x > -50]

        # --- DRAWING ---
        screen.fill(NIGHT_BLUE)
        for lit in city_lights: pygame.draw.circle(screen, (70, 70, 100), (int(lit[0]), int(lit[1])), 1)
        for b in state["scenery"]: b.draw(screen)
        for d in state["doodads"]: d.draw(screen)
        pygame.draw.rect(screen, ASPHALT, (0, LANE_TOP, WIDTH, LANE_BOTTOM - LANE_TOP))
        pygame.draw.rect(screen, NEON_PURPLE, (0, LANE_TOP, WIDTH, 3)); pygame.draw.rect(screen, NEON_PURPLE, (0, LANE_BOTTOM, WIDTH, 3))
        off = (now // 20) % 100 if state["active"] else 0
        for x in range(-100, WIDTH+100, 100): 
            pygame.draw.rect(screen, (40,40,70), (x-off, 285, 40, 2)); pygame.draw.rect(screen, (40,40,70), (x-off, 405, 40, 2))
        for p in state["powerups"]: screen.blit(slow_img if p["type"] == "SLOW" else emp_img, p["rect"])
        for o in state["obstacles"]:
            screen.blit(enemy_img, o["rect"])
            if o["emp"]: pygame.draw.rect(screen, NEON_CYAN, o["rect"], 3, 6)
        screen.blit(player_img, state["player_rect"])
        for pk in ["police_a", "police_b"]:
            p = state[pk]; (screen.blit(police_img, p["rect"]) if p["rect"].right > 0 else None)
            if p["rect"].right > 0:
                sc = POLICE_RED if (now // 150) % 2 == 0 else POLICE_BLUE
                pygame.draw.rect(screen, sc, (p["rect"].x+10, p["rect"].y-6, 40, 7))
        if state["active"] and state["emp_timer"] > 0:
            pygame.draw.circle(screen, NEON_CYAN, state["player_rect"].center, int((70-state["emp_timer"])*18), 4)

        hud = pygame.Surface((WIDTH, 70), pygame.SRCALPHA); hud.fill((0,0,0,180)); screen.blit(hud, (0,0))
        f = pygame.font.SysFont("monospace", 22, True)
        screen.blit(f.render(f"SCORE: {state['score']}", True, WHITE), (25, 20))
        screen.blit(f.render(f"{state['kmh']:.0f} KMH", True, NEON_CYAN if state['kmh'] < 150 else NEON_PINK), (WIDTH-140, 20))
        if state["wanted_level"] > 0:
            for i in range(state["wanted_level"]): screen.blit(star_img, (WIDTH//2-40+(i*35), 18))

        if not state["active"]:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill(OVERLAY_COLOR); screen.blit(overlay, (0, 0))
            alpha = int(155 + 100 * math.sin(now * 0.005))
            t_surf = pygame.font.SysFont("monospace", 75, True).render(state["fail_reason"], True, NEON_PINK); t_surf.set_alpha(alpha)
            screen.blit(t_surf, (WIDTH//2-t_surf.get_width()//2, HEIGHT//2-100))
            s_f = pygame.font.SysFont("monospace", 30, True); screen.blit(s_f.render(f"FINAL SCORE: {state['score']}", True, WHITE), (WIDTH//2-140, HEIGHT//2))
            screen.blit(s_f.render(f"TOP SPEED: {state['max_kmh']:.0f} KMH", True, NEON_CYAN), (WIDTH//2-140, HEIGHT//2 + 40))
            r = pygame.font.SysFont("monospace", 22, True).render("PRESS 'R' TO RESTART", True, WHITE)
            screen.blit(r, (WIDTH//2-r.get_width()//2, HEIGHT//2+110))

    pygame.display.flip(); clock.tick(60)