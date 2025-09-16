# ==============================================================================
# 1. IMPORT LIBRARIES
# ==============================================================================
import cv2
import pygame
import pyautogui
from hand_tracker import HandTracker
from gestures import is_fist, is_open_palm

pyautogui.FAILSAFE = False

# ==============================================================================
# 2. INITIAL SETUP & CONSTANTS
# ==============================================================================
# --- ตั้งค่ากล้องและขนาดหน้าจออัตโนมัติ ---
# <<<<<<<<<<<<<<<<<<<< CHANGE POINT 1: DYNAMIC SCREEN SIZE >>>>>>>>>>>>>>>>>>>>
cap = cv2.VideoCapture(0)
# อ่านเฟรมแรกเพื่อเอาขนาดจริงๆ ของกล้อง
ret, frame = cap.read()
if not ret:
    print("Cannot open camera!")
    exit()
SCREEN_HEIGHT, SCREEN_WIDTH, _ = frame.shape
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# --- ตั้งค่าหน้าจอ Pygame ตามขนาดกล้อง ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Keyboard Gesture Controller v2.2")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24, bold=True)
font_status = pygame.font.SysFont("Arial", 28, bold=True)

# --- ตั้งค่า Hand Tracker ---
tracker = HandTracker(max_num_hands=2, detection_conf=0.8, tracking_conf=0.8)

# --- ตั้งค่าโซนคีย์บอร์ด ---
KEYS = ['a', 's', 'd', 'g', 'h']
NUM_KEYS = len(KEYS)
ZONE_AREA_HEIGHT = SCREEN_HEIGHT // 2
ZONE_WIDTH = SCREEN_WIDTH // NUM_KEYS


def draw_hand_status(screen, hand):
    """วาดสถานะของมือ (FIST, OPEN) ใกล้ๆ ข้อมือเพื่อการดีบัก"""
    if not hand: return
    
    wrist_pos = hand["landmarks"][0]
    status = "UNKNOWN"
    color = (200, 200, 200)

    if is_fist(hand["landmarks"]):
        status = "FIST"
        color = (255, 100, 100) # Red
    elif is_open_palm(hand["landmarks"]):
        status = "OPEN"
        color = (100, 255, 100) # Green
    
    text_surf = font.render(status, True, color)
    screen.blit(text_surf, (wrist_pos[0] + 15, wrist_pos[1] + 15))


# ==============================================================================
# 3. KeyZone Class
# ==============================================================================
class KeyZone:
    def __init__(self, x, key):
        self.x = x
        self.width = ZONE_WIDTH
        self.key = key
        self.rect = pygame.Rect(x, 0, ZONE_WIDTH, ZONE_AREA_HEIGHT)
        self.is_held = False
        self.hand_in_zone = False
        self.last_tap_time = 0
        self.palm_hover_start_time = 0
        self.sustain_activated = False
        self.color_idle = (255, 255, 255, 50)
        self.color_hover = (255, 255, 0, 100)
        self.color_held = (100, 255, 100, 150)

    def update(self, hand_landmarks, status_callback):
        hand_pos = hand_landmarks[8] if hand_landmarks else None
        currently_in_zone = self.rect.collidepoint(hand_pos) if hand_pos else False
        current_time = pygame.time.get_ticks()

        if currently_in_zone:
            if is_open_palm(hand_landmarks):
                if self.palm_hover_start_time == 0: self.palm_hover_start_time = current_time
                if current_time - self.palm_hover_start_time > 1000 and not self.sustain_activated:
                    if not self.is_held:
                        self.is_held = True
                        pyautogui.keyDown(self.key)
                        status_callback(f"SUSTAIN: {self.key.upper()}")
                    else:
                        self.is_held = False
                        pyautogui.keyUp(self.key)
                        status_callback(f"RELEASE: {self.key.upper()}")
                    self.sustain_activated = True
            else:
                self.palm_hover_start_time = 0
                self.sustain_activated = False

            if not is_open_palm(hand_landmarks) and not is_fist(hand_landmarks) and not self.is_held and current_time - self.last_tap_time > 500:
                pyautogui.press(self.key, interval=0.05)
                self.last_tap_time = current_time
                status_callback(f"TAP: {self.key.upper()}")
        
        if not currently_in_zone:
            self.palm_hover_start_time = 0
            self.sustain_activated = False
        self.hand_in_zone = currently_in_zone

    def draw(self, screen):
        color = self.color_idle
        if self.is_held: color = self.color_held
        elif self.hand_in_zone: color = self.color_hover
        s = pygame.Surface((self.width, ZONE_AREA_HEIGHT), pygame.SRCALPHA)
        s.fill(color)
        screen.blit(s, (self.x, 0))
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        text_surf = font.render(self.key.upper(), True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, 40))
        screen.blit(text_surf, text_rect)


# ==============================================================================
# 4. OBJECT CREATION & STATE VARIABLES
# ==============================================================================
key_zones = [KeyZone(i * ZONE_WIDTH, KEYS[i]) for i in range(NUM_KEYS)]
status_text = ""
status_timer = 0

def set_status(text):
    global status_text, status_timer
    status_text = text
    status_timer = 90

# ==============================================================================
# 5. MAIN GAME LOOP
# ==============================================================================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    # เราสามารถให้ tracker วาดเส้นได้เลย เพราะตอนนี้ขนาดภาพกับจอเท่ากันแล้ว
    frame_with_landmarks, all_hands = tracker.get_landmarks(frame, draw=True)

    left_hand, right_hand = None, None
    for hand in all_hands:
        if hand["landmarks"][0][0] < SCREEN_WIDTH / 2:
            left_hand = hand
        else:
            right_hand = hand

    for zone in key_zones:
        zone.update(left_hand["landmarks"] if left_hand else None, set_status)

    left_fist = is_fist(left_hand["landmarks"]) if left_hand else False
    right_fist = is_fist(right_hand["landmarks"]) if right_hand else False
    if left_fist and right_fist:
        keys_were_held = False
        for zone in key_zones:
            if zone.is_held:
                keys_were_held = True
                zone.is_held = False
                pyautogui.keyUp(zone.key)
        if keys_were_held:
            set_status("STOP ALL")
            pygame.time.delay(500)

    # --- Drawing ---
    # <<<<<<<<<<<<<<<<<<<< CHANGE POINT 2: SIMPLIFIED DRAWING >>>>>>>>>>>>>>>>>>>>
    # แปลงภาพและวาดลงจอตรงๆ ไม่ต้องมี scaling
    frame_rgb = cv2.cvtColor(frame_with_landmarks, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0,0))
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    for zone in key_zones:
        zone.draw(screen)
    
    draw_hand_status(screen, left_hand)
    draw_hand_status(screen, right_hand)

    if status_timer > 0:
        status_surf = font_status.render(status_text, True, (255, 255, 0))
        screen.blit(status_surf, (20, SCREEN_HEIGHT - 50))
        status_timer -= 1

    pygame.display.flip()
    clock.tick(30)

# --- CLEANUP ---
for zone in key_zones:
    if zone.is_held:
        pyautogui.keyUp(zone.key)
cap.release()
pygame.quit()