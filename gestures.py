import math

def check_pinch(landmarks):
    """
    ตรวจจับท่าทางการหนีบนิ้วระหว่างนิ้วโป้งกับนิ้วชี้
    และคืนค่าสถานะ "pinching" และระยะห่าง
    """
    if not landmarks or len(landmarks) < 9:
        return False, -1

    # Thumb tip (4), index tip (8)
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]

    # คำนวณระยะห่าง
    distance = math.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)

    # ถ้าหนีบนิ้วใกล้กันพอสมควร
    if distance < 35: # ค่านี้อาจจะต้องปรับจูน
        return True, distance
    
    return False, distance

def is_fist(landmarks):
    """
    ตรวจจับท่ากำปั้น
    โดยเช็คว่าปลายนิ้ว (ชี้, กลาง, นาง, ก้อย) อยู่ใกล้กับฝ่ามือหรือไม่
    """
    if not landmarks or len(landmarks) < 21:
        return False

    # Landmark ของฝ่ามือ (ใช้เป็นจุดอ้างอิง)
    palm_center = landmarks[9] 

    # Landmark ของปลายนิ้ว
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Landmark ของโคนนิ้ว (เพื่อใช้เทียบระยะ)
    index_mcp = landmarks[5]

    # คำนวณระยะอ้างอิง: ระยะห่างระหว่างโคนนิ้วชี้กับปลายนิ้วชี้ตอนเหยียดตรง (โดยประมาณ)
    # เราจะใช้ระยะห่างระหว่างข้อมือกับโคนนิ้วชี้เป็นตัวแทนความยาวของฝ่ามือ
    wrist = landmarks[0]
    ref_distance = math.sqrt((wrist[0] - index_mcp[0])**2 + (wrist[1] - index_mcp[1])**2)


    # เช็คว่าปลายนิ้วทั้งหมดอยู่ใกล้ฝ่ามือมากกว่าระยะอ้างอิงหรือไม่
    # เราลดทอน ref_distance ลงเล็กน้อย (เช่น * 0.8) เพื่อให้แน่ใจว่านิ้วงอเข้ามาจริงๆ
    threshold = ref_distance * 0.7 

    d_index = math.sqrt((index_tip[0] - palm_center[0])**2 + (index_tip[1] - palm_center[1])**2)
    d_middle = math.sqrt((middle_tip[0] - palm_center[0])**2 + (middle_tip[1] - palm_center[1])**2)
    d_ring = math.sqrt((ring_tip[0] - palm_center[0])**2 + (ring_tip[1] - palm_center[1])**2)
    d_pinky = math.sqrt((pinky_tip[0] - palm_center[0])**2 + (pinky_tip[1] - palm_center[1])**2)
    
    return d_index < threshold and d_middle < threshold and d_ring < threshold and d_pinky < threshold