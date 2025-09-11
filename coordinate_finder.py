import pyautogui
import time

print("โปรแกรมจะเริ่มหาพิกัดใน 5 วินาที...")
print("เลื่อนเมาส์ไปชี้ที่ปุ่มที่ต้องการ แล้วรอจนกว่าพิกัดจะแสดงผล")
print("กด Ctrl+C ในหน้าต่างนี้เพื่อจบโปรแกรม")

try:
    while True:
        time.sleep(5)  # รอ 5 วินาที
        x, y = pyautogui.position()
        print(f"พิกัดปัจจุบัน: X={x} Y={y}")
except KeyboardInterrupt:
    print("\nจบโปรแกรม")