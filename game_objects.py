import pygame
import random
import time
import math

class HitCircle:
    def __init__(self, screen_width, screen_height, number):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = 40
        self.pos = self.get_random_pos()
        self.number = number
        self.font = pygame.font.SysFont(None, 50)
        
        # Colors
        self.active_color = (255, 105, 180) # สีชมพู
        self.hit_color = (255, 215, 0) # สีเหลืองทอง

        # Timing
        self.lifetime = random.uniform(5.0, 8.0) 
        self.creation_time = time.time()
        self.approach_rate = 3  
        self.approach_circle_radius = self.radius * 4

        self.state = "active" # สถานะ: active, hit, miss
        self.hit_time = 0

    def get_random_pos(self):
        """สุ่มตำแหน่งบนหน้าจอโดยไม่ให้ชิดขอบเกินไป"""
        x = random.randint(self.radius, self.screen_width - self.radius)
        y = random.randint(self.radius, self.screen_height - self.radius)
        return [x, y]

    def update(self):
        """อัปเดตสถานะและ Approach Circle"""
        if self.state == "active":
            elapsed_time = time.time() - self.creation_time
            # อัปเดตขนาดของ Approach Circle
            self.approach_circle_radius = self.radius + (self.radius * 3 * (1 - (elapsed_time * self.approach_rate / self.lifetime)))
            if self.approach_circle_radius < self.radius:
                self.approach_circle_radius = self.radius

            # เช็คว่าหมดเวลาหรือยัง
            if elapsed_time > self.lifetime:
                self.state = "miss"
        
        # ถ้าโดนตีแล้ว ให้รอแปปนึงแล้วค่อยหายไป
        if self.state == "hit" and time.time() - self.hit_time > 0.3:
            self.state = "to_be_removed"


    def draw(self, screen):
        """วาด HitCircle และองค์ประกอบต่างๆ"""
        current_color = self.hit_color if self.state == "hit" else self.active_color
        current_radius = self.radius

        # ถ้าโดนตี ให้มี animation หดลงเล็กน้อย
        if self.state == "hit":
            time_since_hit = time.time() - self.hit_time
            shrink_factor = 1 - (time_since_hit / 0.3)
            current_radius = int(self.radius * shrink_factor)
            if current_radius < 0: current_radius = 0
        
        # วาด Approach Circle (ถ้ายังไม่โดนตี)
        if self.state == "active":
            pygame.draw.circle(screen, current_color, self.pos, int(self.approach_circle_radius), 3)

        # วาดตัววงกลมหลัก
        pygame.draw.circle(screen, current_color, self.pos, current_radius)
        pygame.draw.circle(screen, (0, 0, 0), self.pos, current_radius, 2) # ขอบดำ

        # วาดตัวเลข (ถ้ายังไม่โดนตี)
        if self.state == "active":
            text_surface = self.font.render(str(self.number), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=self.pos)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, point):
        """เช็คว่าจุดที่คลิกอยู่ในวงกลมหรือไม่"""
        if not point or self.state != "active":
            return False
        dx = point[0] - self.pos[0]
        dy = point[1] - self.pos[1]
        return dx*dx + dy*dy <= self.radius * self.radius

    def get_timing_score(self):
        """คำนวณคะแนนตามจังหวะการคลิก"""
        timing_window = abs(self.approach_circle_radius - self.radius)
        
        if timing_window <= 10: # Perfect
            return 10, "Perfect"
        elif timing_window <= 25: # Great
            return 7, "Great"
        else: # Good
            return 3, "Good"
    
    def on_hit(self):
        """เปลี่ยนสถานะเมื่อถูกตี"""
        if self.state == "active":
            self.state = "hit"
            self.hit_time = time.time()