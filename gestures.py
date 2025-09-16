import math

def is_fist(landmarks):
    """
    ตรวจจับท่ากำปั้น
    โดยเช็คว่าปลายนิ้ว (ชี้, กลาง, นาง, ก้อย) อยู่ใกล้กับฝ่ามือหรือไม่
    คืนค่า: True ถ้าเป็นกำปั้น, False ถ้าไม่ใช่
    """
    if not landmarks or len(landmarks) < 21:
        return False

    # Landmark ของฝ่ามือ (ใช้เป็นจุดอ้างอิง)
    palm_center = landmarks[9] 

    # Landmark ของปลายนิ้ว
    tips = [landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
    
    # Landmark ของโคนนิ้ว (เพื่อใช้เทียบระยะ)
    mcp_joints = [landmarks[5], landmarks[9], landmarks[13], landmarks[17]]
    
    # คำนวณระยะอ้างอิง: ใช้ระยะเฉลี่ยจากฝ่ามือถึงโคนนิ้วเป็นตัวแทนขนาดฝ่ามือ
    try:
        ref_distance = sum(math.dist(palm_center, joint) for joint in mcp_joints) / len(mcp_joints)
    except IndexError:
        return False

    # กำหนด Threshold: ถ้าปลายนิ้วเข้ามาใกล้ฝ่ามือมากกว่าระยะอ้างอิงเล็กน้อย ถือว่ากำหมัด
    # เราใช้ 1.2 เพื่อให้มีระยะเผื่อเล็กน้อย
    threshold = ref_distance * 1.2

    # เช็คว่าปลายนิ้วทั้งหมดอยู่ใกล้ฝ่ามือกว่า threshold หรือไม่
    for tip in tips:
        distance = math.dist(tip, palm_center)
        if distance > threshold:
            return False # หากมีนิ้วใดยื่นออกไปไกลเกิน ให้ถือว่าไม่ใช่กำปั้น
            
    return True

def is_open_palm(landmarks):
    """
    ตรวจจับท่าแบมือ
    โดยเช็คว่าปลายนิ้วทั้งหมดเหยียดออกและอยู่ห่างจากฝ่ามือ
    คืนค่า: True ถ้าแบมือ, False ถ้าไม่ใช่
    """
    if not landmarks or len(landmarks) < 21:
        return False

    # Landmark ของฝ่ามือ (ใช้เป็นจุดอ้างอิง)
    palm_center = landmarks[9] 

    # Landmark ของปลายนิ้ว
    tips = [landmarks[8], landmarks[12], landmarks[16], landmarks[20]]
    
    # Landmark ของโคนนิ้ว
    mcp_joints = [landmarks[5], landmarks[9], landmarks[13], landmarks[17]]

    # คำนวณระยะอ้างอิงเหมือนฟังก์ชัน is_fist
    try:
        ref_distance = sum(math.dist(palm_center, joint) for joint in mcp_joints) / len(mcp_joints)
    except IndexError:
        return False
        
    # กำหนด Threshold: ถ้าปลายนิ้วอยู่ห่างจากฝ่ามือมากกว่าระยะอ้างอิงคูณ 2.5 แสดงว่าน่าจะเหยียดตรง
    threshold = ref_distance * 2.5

    # เช็คว่าปลายนิ้วทั้งหมดอยู่ไกลจากฝ่ามือมากกว่า threshold หรือไม่
    for tip in tips:
        distance = math.dist(tip, palm_center)
        if distance < threshold:
            return False # หากมีนิ้วใดงอเข้ามาใกล้เกินไป ถือว่าไม่ได้แบมือ
            
    return True