import cv2
import pygame
import math
from hand_tracker import HandTracker
from gestures import is_fist

# --- 1. การตั้งค่า ---
# ตั้งค่าหน้าจอ Pygame
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
pygame.init()
pygame.mixer.init() # เริ่มต้นระบบเสียง
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gesture Soundboard")
clock = pygame.time.Clock()
font_chord = pygame.font.SysFont("Arial", 22, bold=True)
font_info = pygame.font.SysFont("Arial", 24)

# ตั้งค่ากล้องและ Hand Tracker
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_HEIGHT)
tracker = HandTracker(max_num_hands=2)

# --- 2. ตั้งค่าคอร์ดและเสียง ---
CHORD_NAMES = [
    "E", "Fsm", "Gsm", "A", "B", "Csm", "Ebdim", 
    "E_h", "Fsm_h", "Gsm_h", "A_h"
]

# โหลดไฟล์เสียง (ต้องมีโฟลเดอร์ sounds และไฟล์เสียงที่ชื่อตรงกัน)
try:
    CHORD_SOUNDS = {name: pygame.mixer.Sound(f"/home/eggchad160606/project/ait_work/com_vision/python/mini_project/source/{name}.wav") for name in CHORD_NAMES}
except pygame.error as e:
    print(f"Error loading sound files: {e}")
    print("Please make sure you have a 'sounds' folder with all 11 .wav files.")
    # สร้างเสียงเปล่าๆ เพื่อให้โปรแกรมรันต่อได้ แต่จะไม่มีเสียง
    CHORD_SOUNDS = {}

# --- 3. คลาสสำหรับ UI วงกลมคอร์ด ---
class ChordCircle:
    def __init__(self, x, y, radius, chord_name, sound):
        self.x, self.y = x, y
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.chord_name = chord_name
        self.sound = sound
        
        self.is_playing = False
        self.is_hovered = False
        
        # Colors
        self.color_idle = (100, 100, 255) # สีน้ำเงิน
        self.color_hover = (255, 180, 105) # สีส้ม
        self.color_playing = (100, 255, 100) # สีเขียว
        self.font_color = (255, 255, 255)

    def update(self, hand_pos):
        # เช็คว่ามือมาโดนวงกลมหรือไม่
        self.is_hovered = self.rect.collidepoint(hand_pos) if hand_pos else False

        if self.is_hovered and not self.is_playing and self.sound:
            # เริ่มเล่นเสียงแบบวนลูป
            self.sound.play(loops=-1)
            self.is_playing = True
        elif not self.is_hovered and self.is_playing and self.sound:
            # หยุดเล่นเสียงแบบ fade out
            self.sound.fadeout(1500) # ค่อยๆ เบาลงใน 1.5 วินาที
            self.is_playing = False

    def draw(self, screen):
        current_color = self.color_idle
        if self.is_playing:
            current_color = self.color_playing
        elif self.is_hovered:
            current_color = self.color_hover
            
        pygame.draw.circle(screen, current_color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius, 3) # ขอบขาว

        # แสดงชื่อคอร์ด
        text_surf = font_chord.render(self.chord_name, True, self.font_color)
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, text_rect)

# --- 4. สร้าง UI คอร์ด ---
chord_circles = []
RADIUS = 50
START_Y = 70
SPACING_Y = 65
X_POS1 = 80
X_POS2 = 160
for i, name in enumerate(CHORD_NAMES):
    x_pos = X_POS1 if (i // 2) % 2 == 0 else X_POS2
    y_pos = START_Y + (i * SPACING_Y)
    
    # ทำให้วงกลมสุดท้ายไม่ตกขอบล่าง
    if y_pos > SCREEN_HEIGHT - RADIUS:
       y_pos -= (len(CHORD_NAMES) - i) * SPACING_Y # ย้ายแถวขึ้น
       x_pos += 100

    sound = CHORD_SOUNDS.get(name) # ใช้ .get เพื่อป้องกัน error ถ้าโหลดเสียงไม่สำเร็จ
    chord_circles.append(ChordCircle(x_pos, y_pos % (SCREEN_HEIGHT - RADIUS), RADIUS, name, sound))


# --- 5. Game Loop หลัก ---
running = True
master_volume = 1.0

while running:
    # --- การรับภาพและหา Landmark ---
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame_with_landmarks, all_hands = tracker.get_landmarks(frame, draw=True)

    # --- การประมวลผลท่าทาง ---
    left_hand, right_hand = None, None
    for hand in all_hands:
        if hand["handedness"] == "Left":
            left_hand = hand
        elif hand["handedness"] == "Right":
            right_hand = hand

    # มือซ้าย: เลือกและเล่นคอร์ด
    left_hand_pos = left_hand["landmarks"][8] if left_hand else None # ใช้ปลายนิ้วชี้
    for circle in chord_circles:
        circle.update(left_hand_pos)
    
    # มือขวา: ควบคุมความดัง
    if right_hand:
        wrist_y = right_hand["landmarks"][0][1]
        # map ค่า y (0 ถึง SCREEN_HEIGHT) ไปเป็น volume (1.0 ถึง 0.0)
        master_volume = 1.0 - (wrist_y / SCREEN_HEIGHT)
        if master_volume < 0: master_volume = 0.0
        if master_volume > 1: master_volume = 1.0
        
        # ตั้งค่าความดังให้ทุก Channel
        pygame.mixer.set_num_channels(50) # เพิ่มจำนวนช่องเสียงเผื่อไว้
        for i in range(pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).set_volume(master_volume)

    # สองมือ: กำหมัดเพื่อหยุดทุกอย่าง
    left_fist = is_fist(left_hand["landmarks"]) if left_hand else False
    right_fist = is_fist(right_hand["landmarks"]) if right_hand else False
    if left_fist and right_fist:
        pygame.mixer.stop()
        for circle in chord_circles:
            circle.is_playing = False # รีเซ็ตสถานะ

    # --- การแสดงผลบน Pygame ---
    # แสดงภาพจากกล้อง
    frame_rgb = cv2.cvtColor(frame_with_landmarks, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    screen.blit(frame_surface, (0, 0))

    # วาด UI คอร์ด
    for circle in chord_circles:
        circle.draw(screen)

    # วาดแถบ Volume
    vol_bar_height = master_volume * (SCREEN_HEIGHT - 40)
    pygame.draw.rect(screen, (255, 255, 255, 150), [SCREEN_WIDTH - 50, 20, 30, SCREEN_HEIGHT - 40], 2, border_radius=5)
    pygame.draw.rect(screen, (100, 255, 100, 200), [SCREEN_WIDTH - 45, (SCREEN_HEIGHT-20) - vol_bar_height, 20, vol_bar_height], border_radius=5)


    # --- จัดการ Event และอัปเดตหน้าจอ ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(30)

# --- สิ้นสุดโปรแกรม ---
cap.release()
pygame.quit()