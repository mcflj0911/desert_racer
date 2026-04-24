import pygame
import random
import sys
import os
import math

# --- 1. Initialization ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doodads")

# --- 2. Constants (UPDATED FOR 1400x800) ---
WIDTH, HEIGHT = 1400, 800  
CAR_SIZE = 60
BASE_GAME_SPEED = 6.0     

# Road area expanded: 5 Lanes instead of 4
LANE_TOP, LANE_BOTTOM = 200, 720 
# Spaced out for 5 distinct lanes
LANES = [240, 330, 420, 510, 600] 

# Colors
NIGHT_BLUE = (15, 10, 25); ASPHALT = (10, 10, 15)         
NEON_PINK = (255, 20, 147); NEON_CYAN = (0, 255, 255)      
NEON_PURPLE = (150, 0, 255); WHITE = (240, 240, 255)
NEON_ORANGE = (255, 100, 0); GLOW_YELLOW = (255, 255, 0)
OVERLAY_COLOR = (5, 5, 15, 235); POLICE_RED = (255, 0, 50); POLICE_BLUE = (0, 50, 255)
OIL_BLACK = (20, 20, 30)
WIND_COLOR = (200, 230, 255, 40) # Semi-transparent light blue for wind

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desert Pixel Racer - Extreme Widescreen")
clock = pygame.time.Clock()

# --- 3. Asset Loading ---
def get_image(name, size_or_tuple, fallback_color):
    full_path = os.path.join(BASE_PATH, name)
    target_size = (size_or_tuple, size_or_tuple) if isinstance(size_or_tuple, int) else size_or_tuple
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, target_size)
        except: pass
    surf = pygame.Surface(target_size, pygame.SRCALPHA)
    pygame.draw.rect(surf, fallback_color, (0, 0, target_size[0], target_size[1]), border_radius=10)
    pygame.draw.rect(surf, WHITE, (0, 0, target_size[0], target_size[1]), 2, border_radius=10)
    return surf

player_img = get_image("player_car.png", CAR_SIZE, NEON_PINK)
enemy_img = get_image("obstacle_car.png", CAR_SIZE, NEON_PURPLE)
police_img = get_image("police_car.png", CAR_SIZE, (45, 45, 60))
cactus_img = get_image("cactus.png", 50, (30, 120, 30))
rock_img = get_image("rock.png", 40, (140, 110, 90))
star_img = get_image("star.png", 32, (255, 255, 0))
slow_img = get_image("slow_down.png", 40, (0, 255, 100))
emp_img = get_image("emp.png", 40, NEON_CYAN)
rocket_p_img = get_image("rocket_powerup.png", 40, NEON_ORANGE)
oil_spill_img = get_image("oil.png", (65, 40), OIL_BLACK)

def load_sfx(name):
    path = os.path.join(BASE_PATH, name)
    return pygame.mixer.Sound(path) if os.path.exists(path) else None

crash_sfx = load_sfx("crash.mp3"); slow_sfx = load_sfx("slow.mp3"); emp_sfx = load_sfx("emp.mp3")
beep_sfx = load_sfx("beep.mp3"); rocket_launch_sfx = load_sfx("rocket_launch.mp3")
rocket_pick_sfx = load_sfx("rocket_pick.mp3"); screech_sfx = load_sfx("screech.mp3")

music_path = os.path.join(BASE_PATH, "music.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path); pygame.mixer.music.set_volume(0.4); pygame.mixer.music.play(-1)

# --- 4. Logic Classes ---
class WindGust:
    def __init__(self):
        self.reset()
        self.x = random.randint(0, WIDTH) # Initial random spread

    def reset(self):
        self.x = WIDTH + random.randint(10, 500)
        self.y = random.randint(0, HEIGHT)
        self.length = random.randint(40, 120)
        self.thickness = random.randint(1, 3)
        self.speed_mult = random.uniform(1.2, 2.5)

    def update(self, game_speed):
        self.x -= game_speed * self.speed_mult
        if self.x + self.length < 0:
            self.reset()

    def draw(self, surf):
        # Wind is a semi-transparent line
        wind_surf = pygame.Surface((self.length, self.thickness), pygame.SRCALPHA)
        wind_surf.fill(WIND_COLOR)
        surf.blit(wind_surf, (self.x, self.y))

class OilSpill:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(LANE_TOP + 10, LANE_BOTTOM - 50)
        self.rect = pygame.Rect(self.x, self.y, 65, 40)

    def update(self, speed): 
        self.x -= speed
        self.rect.x = self.x

    def draw(self, surf): 
        surf.blit(oil_spill_img, (self.rect.x, self.rect.y))
        now = pygame.time.get_ticks()
        pulse = (math.sin(now * 0.01) + 1) / 2
        r = int(NEON_ORANGE[0] + (GLOW_YELLOW[0] - NEON_ORANGE[0]) * pulse)
        g = int(NEON_ORANGE[1] + (GLOW_YELLOW[1] - NEON_ORANGE[1]) * pulse)
        b = int(NEON_ORANGE[2] + (GLOW_YELLOW[2] - NEON_ORANGE[2]) * pulse)
        pygame.draw.rect(surf, (r, g, b), self.rect.inflate(4, 4), 2, border_radius=15)

class Rocket:
    def __init__(self, x, y): self.rect = pygame.Rect(x, y, 30, 10)
    def update(self): self.rect.x += 15
    def draw(self, surf):
        pygame.draw.rect(surf, NEON_ORANGE, self.rect, border_radius=3)
        pygame.draw.rect(surf, WHITE, self.rect, 1, border_radius=3)

class Building:
    def __init__(self, x):
        self.width = random.randint(120, 200); self.height = random.randint(300, 500)
        self.x = x; self.y = LANE_TOP - self.height; self.color = (30, 25, 45)
        self.windows = [(random.randint(5, self.width-12), random.randint(10, self.height-20)) for _ in range(25)]
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.width, self.height))
        for wx, wy in self.windows:
            w_col = (255, 255, 180) if random.random() > 0.1 else (20, 20, 40)
            pygame.draw.rect(surf, w_col, (self.x + wx, self.y + wy, 6, 8))

class Doodad:
    def __init__(self, x, img):
        self.img = img; side = random.choice(["top", "bottom"])
        if side == "top": self.y = random.randint(LANE_TOP - 60, LANE_TOP - 45) 
        else: self.y = random.randint(LANE_BOTTOM + 5, LANE_BOTTOM + 20)
        self.x = x; self.rect = pygame.Rect(self.x, self.y, img.get_width(), img.get_height())
    def draw(self, surf): surf.blit(self.img, (self.x, self.y))

def draw_car_lights(surf, rect, is_emp=False):
    if is_emp: return 
    light_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    beam_length, beam_width = 180, 50
    beam_color = (115, 155, 0, 90) 
    headlights = [(rect.right - 2, rect.top + 12), (rect.right - 2, rect.bottom - 12)]
    for h_pos in headlights:
        points = [h_pos, (h_pos[0] + beam_length, h_pos[1] - beam_width), (h_pos[0] + beam_length, h_pos[1] + beam_width)]
        pygame.draw.polygon(light_layer, beam_color, points)
    surf.blit(light_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    t_glow = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(t_glow, (180, 0, 0, 90), (20, 20), 10)
    surf.blit(t_glow, (rect.left - 15, rect.centery - 20))

def is_space_clear(new_rect, current_state, min_dist=200): 
    for obs in current_state["obstacles"]:
        if new_rect.colliderect(obs["rect"].inflate(min_dist, 20)): return False
    for p in current_state["powerups"]:
        if new_rect.colliderect(p["rect"].inflate(min_dist, 20)): return False
    for d in current_state["doodads"]:
        if new_rect.colliderect(d.rect.inflate(50, 50)): return False
    for spill in current_state["oil_spills"]:
        if new_rect.colliderect(spill.rect.inflate(60, 60)): return False
    return True

def reset_game(diff="NORMAL"):
    sr, psr = (1000, 2500) if diff=="EASY" else ((400, 5000) if diff=="HARD" else (700, 3500))
    return {
        "active": True, "difficulty": diff, "score": 0, "spawn_rate": sr, "powerup_rate": psr,
        "current_speed": BASE_GAME_SPEED, "speed_modifier": 1.0, "lane_offset": 0,
        "kmh": 0, "max_kmh": 0, "ammo": 0, "player_rect": pygame.Rect(150, HEIGHT//2, CAR_SIZE, CAR_SIZE),
        "vel_x": 0, "vel_y": 0, "obstacles": [], "powerups": [], "scenery": [], 
        "doodads": [], "rockets": [], "oil_spills": [],
        "wind_particles": [WindGust() for _ in range(25)], # Pool of wind streaks
        # Buffer for 4 active police cars
        "police": [{"rect": pygame.Rect(-160, LANES[i%5], CAR_SIZE, CAR_SIZE), "emp": False, "oil_timer": 0} for i in range(4)],
        "wanted_level": 0, "emp_timer": 0, "player_oil_timer": 0, "fail_reason": ""
    }

def draw_info_box():
    box_rect = pygame.Rect(WIDTH - 380, HEIGHT - 310, 350, 280)
    info_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA); info_surf.fill((0, 0, 0, 180))
    pygame.draw.rect(info_surf, NEON_CYAN, (0, 0, box_rect.width, box_rect.height), 2, border_radius=8)
    screen.blit(info_surf, box_rect)
    f_s = pygame.font.SysFont("monospace", 15, bold=True); h = pygame.font.SysFont("monospace", 18, bold=True)
    y = box_rect.y + 20
    screen.blit(h.render("SYSTEM CONTROLS", True, NEON_CYAN), (box_rect.x + 20, y))
    screen.blit(f_s.render("> WASD / ARROWS : DRIVE", True, WHITE), (box_rect.x + 20, y+25))
    screen.blit(f_s.render("> SPACE : FIRE ROCKET / SELECT", True, WHITE), (box_rect.x + 20, y+45))
    screen.blit(f_s.render("> OIL SPILLS : TRACTION LOSS", True, NEON_ORANGE), (box_rect.x + 20, y+65))
    screen.blit(h.render("POWERUPS", True, NEON_CYAN), (box_rect.x + 20, y+100))
    screen.blit(f_s.render("> GREEN: SLOW-MO SPEED", True, (0, 255, 100)), (box_rect.x + 20, y+125))
    screen.blit(f_s.render("> CYAN : EMP DISRUPTION", True, NEON_CYAN), (box_rect.x + 20, y+145))
    screen.blit(f_s.render("> ORANGE: +3 ROCKETS", True, NEON_ORANGE), (box_rect.x + 20, y+165))

# --- 5. Main Execution ---
state = reset_game(); game_mode = "MENU"; menu_selection = 1; last_key_time = 0
city_lights = [[random.randint(0, WIDTH), random.randint(0, LANE_TOP)] for _ in range(80)]

last_s = 0; last_p = 0
while True:
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if game_mode == "GAME":
            if state["active"] and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if state["ammo"] > 0:
                    state["rockets"].append(Rocket(state["player_rect"].right, state["player_rect"].centery))
                    state["ammo"] -= 1; (rocket_launch_sfx.play() if rocket_launch_sfx else None)
            elif not state["active"] and event.type == pygame.KEYDOWN and event.key == pygame.K_r: game_mode = "MENU"

    if game_mode == "MENU":
        screen.fill(NIGHT_BLUE)
        sun_center = (WIDTH // 2, 280); pygame.draw.circle(screen, NEON_PINK, sun_center, 150)
        for i in range(8): pygame.draw.rect(screen, NIGHT_BLUE, (WIDTH//2-150, 280 + (i*28), 300, 6+i))
        title_f = pygame.font.SysFont("monospace", 68, bold=True)
        title_t = title_f.render("DESERT PIXEL RACER", True, WHITE)
        screen.blit(title_t, (WIDTH//2 - title_t.get_width()//2, sun_center[1] - 40))
        
        keys = pygame.key.get_pressed()
        if now - last_key_time > 150:
            if keys[pygame.K_w] or keys[pygame.K_UP]: menu_selection = (menu_selection-1)%3; last_key_time = now; (beep_sfx.play() if beep_sfx else None)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: menu_selection = (menu_selection+1)%3; last_key_time = now; (beep_sfx.play() if beep_sfx else None)
        
        btns = [("EASY", 460, NEON_CYAN), ("NORMAL", 540, NEON_PURPLE), ("HARD", 620, NEON_PINK)]
        for i, (txt, y, col) in enumerate(btns):
            is_sel = (menu_selection == i); r = pygame.Rect(WIDTH//2 - 110, y, 220, 60)
            pygame.draw.rect(screen, col if is_sel else (30,30,50), r, border_radius=5)
            bt = pygame.font.SysFont("monospace", 32, True).render(txt, True, WHITE)
            screen.blit(bt, (r.centerx-bt.get_width()//2, r.centery-bt.get_height()//2))
            if is_sel and (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]): state = reset_game(txt); game_mode = "GAME"; last_s = last_p = now
        draw_info_box()

    elif game_mode == "GAME":
        if state["active"]:
            if state["emp_timer"] > 0: state["emp_timer"] -= 1.5
            if state["player_oil_timer"] > 0: state["player_oil_timer"] -= 1
            
            state["lane_offset"] = (state["lane_offset"] + state["current_speed"]) % 100
            base = BASE_GAME_SPEED + (2.1 * math.log(state["score"] + 1))
            if state["speed_modifier"] < 1.0: state["speed_modifier"] += 0.003
            state["current_speed"] = base * state["speed_modifier"]
            state["kmh"] = state["current_speed"] * 15
            if state["kmh"] > state["max_kmh"]: state["max_kmh"] = state["kmh"] 
            
            # Update Wind Particles
            for wind in state["wind_particles"]:
                wind.update(state["current_speed"])

            keys = pygame.key.get_pressed()
            accel = (1.2 + math.log(max(1, state["current_speed"]/BASE_GAME_SPEED))) if state["difficulty"]=="NORMAL" else (1.4 * (1.1**(state["current_speed"]-BASE_GAME_SPEED)) if state["difficulty"]=="HARD" else 1.0)
            
            if keys[pygame.K_w] or keys[pygame.K_UP]: state["vel_y"] -= accel
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: state["vel_y"] += accel
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: state["vel_x"] -= accel
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: state["vel_x"] += accel

            if state["player_oil_timer"] > 0:
                speed_factor = state["current_speed"] * 0.9
                state["vel_x"] += random.uniform(-speed_factor, speed_factor)
                state["vel_y"] += random.uniform(-speed_factor, speed_factor)
            
            state["vel_x"] *= 0.88; state["vel_y"] *= 0.88
            state["player_rect"].x += state["vel_x"]; state["player_rect"].y += state["vel_y"]
            state["player_rect"].y = max(LANE_TOP, min(state["player_rect"].y, LANE_BOTTOM - CAR_SIZE))
            state["player_rect"].x = max(0, min(state["player_rect"].x, WIDTH-CAR_SIZE))
            
            # --- UPDATED POLICE SPAWN LOGIC ---
            if state["kmh"] >= 150:
                state["wanted_level"] = min(4, int((state["kmh"] - 150) // 30) + 1)
            else:
                state["wanted_level"] = 0
            
            player_hitbox = state["player_rect"].inflate(-12, -12)

            for i, p in enumerate(state["police"]):
                if state["wanted_level"] > i and not p["emp"]:
                    oil_offset = random.uniform(-state["current_speed"]*0.5, state["current_speed"]*0.5) if p["oil_timer"] > 0 else 0
                    if p["oil_timer"] > 0: p["oil_timer"] -= 1
                    
                    p_hitbox = p["rect"].inflate(-10, -10)
                    for obs in state["obstacles"]:
                        if not obs["emp"] and p_hitbox.colliderect(obs["rect"].inflate(-12, -12)):
                             p["emp"] = True 
                             p["rect"].x -= 20 
                             (crash_sfx.play() if crash_sfx else None)
                             break
                    
                    if not p["emp"]:
                        p["rect"].y += ((state["player_rect"].y - p["rect"].y) * 0.04) + oil_offset
                        chase_speed = 0.5 if p["oil_timer"] > 0 else 2.0
                        p["rect"].x += chase_speed if (state["player_rect"].x - p["rect"].x) > 150 else 0.6
                        
                        if p["rect"].inflate(-10, -10).colliderect(player_hitbox):
                            state["active"]=False; state["fail_reason"]="BUSTED"; (crash_sfx.play() if crash_sfx else None)
                else:
                    p["rect"].x -= 12
                    if p["rect"].right < -50: p["rect"].x = -160; p["emp"] = False

            if now - last_s > state["spawn_rate"]:
                new_obs = pygame.Rect(WIDTH + 50, random.choice(LANES), CAR_SIZE, CAR_SIZE)
                if is_space_clear(new_obs, state):
                    state["obstacles"].append({"rect": new_obs, "emp": False}); last_s = now
                    if random.random() > 0.5: state["scenery"].append(Building(WIDTH + 150))
                    if random.random() > 0.4: state["doodads"].append(Doodad(WIDTH+50, random.choice([cactus_img, rock_img])))
                    if random.random() > 0.85: state["oil_spills"].append(OilSpill(WIDTH + 50))

            if now - last_p > state["powerup_rate"]:
                new_p = pygame.Rect(WIDTH + 50, random.choice(LANES)+10, 40, 40)
                if is_space_clear(new_p, state): state["powerups"].append({"rect": new_p, "type": random.choice(["SLOW", "EMP", "ROCKET"])}); last_p = now

            for spill in state["oil_spills"][:]:
                spill.update(state["current_speed"])
                # Play screech sound on player collision
                if player_hitbox.colliderect(spill.rect): 
                    if state["player_oil_timer"] == 0: (screech_sfx.play() if screech_sfx else None)
                    state["player_oil_timer"] = 35 
                # Play screech sound on police collision
                for p in state["police"]:
                    if p["rect"].colliderect(spill.rect): 
                        if p["oil_timer"] == 0: (screech_sfx.play() if screech_sfx else None)
                        p["oil_timer"] = 35
                if spill.rect.right < 0: state["oil_spills"].remove(spill)

            for p_up in state["powerups"][:]:
                p_up["rect"].x -= state["current_speed"]
                if player_hitbox.colliderect(p_up["rect"]):
                    if p_up["type"] == "SLOW": state["speed_modifier"] = 0.25; (slow_sfx.play() if slow_sfx else None)
                    elif p_up["type"] == "EMP": 
                        state["emp_timer"] = 80; (emp_sfx.play() if emp_sfx else None)
                        for o in state["obstacles"]: o["emp"] = True
                        for p in state["police"]: p["emp"] = True
                    else: state["ammo"] += 3; (rocket_pick_sfx.play() if rocket_pick_sfx else None)
                    state["powerups"].remove(p_up)

            for obs in state["obstacles"][:]:
                obs["rect"].x -= state["current_speed"]
                if not obs["emp"] and player_hitbox.colliderect(obs["rect"].inflate(-12, -12)):
                    state["active"]=False; state["fail_reason"]="CRASHED"; (crash_sfx.play() if crash_sfx else None)
                if obs["rect"].right < 0: state["obstacles"].remove(obs); state["score"] += 1

            for r in state["rockets"][:]:
                r.update()
                for o in state["obstacles"][:]:
                    if r.rect.colliderect(o["rect"]): 
                        if r in state["rockets"]: state["rockets"].remove(r)
                        state["obstacles"].remove(o); state["score"] += 1; (crash_sfx.play() if crash_sfx else None)
                if r.rect.left > WIDTH: state["rockets"].remove(r)

            for b in state["scenery"]: b.x -= state["current_speed"] * 0.6
            for d in state["doodads"]: d.x -= state["current_speed"] * 0.8; d.rect.x = d.x

        # --- RENDERING SECTION ---
        screen.fill(NIGHT_BLUE)
        for lit in city_lights: pygame.draw.circle(screen, (70, 70, 100), (int(lit[0]), int(lit[1])), 1)
        for b in state["scenery"]: b.draw(screen)
        
        # Road 
        pygame.draw.rect(screen, ASPHALT, (0, LANE_TOP, WIDTH, LANE_BOTTOM - LANE_TOP))
        pygame.draw.line(screen, GLOW_YELLOW, (0, LANE_TOP), (WIDTH, LANE_TOP), 4)
        pygame.draw.line(screen, GLOW_YELLOW, (0, LANE_BOTTOM), (WIDTH, LANE_BOTTOM), 4)
        
        for i in range(1, 5):
            line_y = LANE_TOP + i * ((LANE_BOTTOM - LANE_TOP) // 5)
            for x in range(-100, WIDTH + 100, 80):
                pygame.draw.rect(screen, (50, 50, 80), (x - state["lane_offset"], line_y - 2, 40, 4))
        
        for spill in state["oil_spills"]: spill.draw(screen)
        for d in state["doodads"]: d.draw(screen)
        for p in state["powerups"]:
            p_col = NEON_ORANGE if p["type"]=="ROCKET" else (NEON_CYAN if p["type"]=="EMP" else (0, 255, 100))
            glow = pygame.Surface((100, 100), pygame.SRCALPHA); pygame.draw.circle(glow, (*p_col, 80), (50, 50), 20 + 10 * math.sin(now * 0.01))
            screen.blit(glow, (p["rect"].centerx-50, p["rect"].centery-50))
            screen.blit(slow_img if p["type"]=="SLOW" else (emp_img if p["type"]=="EMP" else rocket_p_img), p["rect"])
        
        for o in state["obstacles"]: draw_car_lights(screen, o["rect"], o["emp"]); screen.blit(enemy_img, o["rect"])
        for r in state["rockets"]: r.draw(screen)
        draw_car_lights(screen, state["player_rect"]); screen.blit(player_img, state["player_rect"])
        
        # --- NEW: WIND GUST RENDERING ---
        # Draw more wind streaks if speed is high
        active_wind_count = min(len(state["wind_particles"]), int(state["kmh"] / 10))
        for i in range(active_wind_count):
            state["wind_particles"][i].draw(screen)

        if state["emp_timer"] > 0:
            sonar_radius = int((80 - state["emp_timer"]) * 15)
            sonar_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = max(0, int(state["emp_timer"] * 3.0))
            pygame.draw.circle(sonar_surf, (*NEON_CYAN, alpha), state["player_rect"].center, sonar_radius, 6)
            screen.blit(sonar_surf, (0, 0))

        for p in state["police"]:
            if p["rect"].right > 0:
                draw_car_lights(screen, p["rect"], p["emp"]); screen.blit(police_img, p["rect"])
                if not p["emp"]:
                    sc = POLICE_RED if (now//150)%2==0 else POLICE_BLUE
                    pg = pygame.Surface((120, 120), pygame.SRCALPHA); pygame.draw.circle(pg, (*sc, 100), (60, 60), 35); screen.blit(pg, (p["rect"].centerx-60, p["rect"].centery-60))

        if state["emp_timer"] > 70: 
            fs = pygame.Surface((WIDTH, HEIGHT)); fs.fill(NEON_CYAN); fs.set_alpha(int((state["emp_timer"]-70)*25)); screen.blit(fs, (0,0))

        # HUD 
        hud = pygame.Surface((WIDTH, 90), pygame.SRCALPHA); hud.fill((0,0,0,190)); screen.blit(hud, (0,0))
        f = pygame.font.SysFont("monospace", 28, True)
        screen.blit(f.render(f"SCORE: {state['score']}", True, WHITE), (40, 30))
        if state["ammo"] > 0: screen.blit(f.render(f"ROCKETS: {state['ammo']}", True, NEON_ORANGE), (280, 30))
        km_c = NEON_ORANGE if state["player_oil_timer"] > 0 else (NEON_CYAN if state['kmh']<150 else NEON_PINK)
        screen.blit(f.render(f"{state['kmh']:.0f} KMH", True, km_c), (WIDTH-220, 30))
        for i in range(state["wanted_level"]): screen.blit(star_img, (WIDTH//2-100+(i*45), 28))

        if not state["active"]:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill(OVERLAY_COLOR); screen.blit(overlay, (0, 0))
            alpha = int(155 + 100 * math.sin(now * 0.005))
            ts = pygame.font.SysFont("monospace", 110, True).render(state["fail_reason"], True, NEON_PINK); ts.set_alpha(alpha)
            screen.blit(ts, (WIDTH//2-ts.get_width()//2, HEIGHT//2-180))
            
            s_f = pygame.font.SysFont("monospace", 36, True)
            diff_col = NEON_CYAN if state["difficulty"]=="EASY" else (NEON_PURPLE if state["difficulty"]=="NORMAL" else NEON_PINK)
            diff_t = s_f.render(f"DIFFICULTY: {state['difficulty']}", True, diff_col)
            score_t = s_f.render(f"FINAL SCORE: {state['score']}", True, WHITE)
            speed_t = s_f.render(f"TOP SPEED: {state['max_kmh']:.0f} KMH", True, NEON_CYAN)
            
            screen.blit(diff_t, (WIDTH//2-diff_t.get_width()//2, HEIGHT//2 - 20))
            screen.blit(score_t, (WIDTH//2-score_t.get_width()//2, HEIGHT//2 + 30))
            screen.blit(speed_t, (WIDTH//2-speed_t.get_width()//2, HEIGHT//2 + 80))
            
            r_t = pygame.font.SysFont("monospace", 30, True).render("PRESS 'R' TO RESTART", True, WHITE)
            screen.blit(r_t, (WIDTH//2-r_t.get_width()//2, HEIGHT//2+180))

    pygame.display.flip(); clock.tick(60)