import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_num_hands=2, detection_conf=0.7, tracking_conf=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands, # <--- แก้ไขตรงนี้เป็น 2
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_landmarks(self, frame, draw=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        
        all_hands_landmarks = []
        if self.results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                hand_info = {
                    "id": hand_idx,
                    "landmarks": [],
                    "handedness": self.results.multi_handedness[hand_idx].classification[0].label
                }
                for lm in hand_landmarks.landmark:
                    h, w, _ = frame.shape
                    hand_info["landmarks"].append((int(lm.x * w), int(lm.y * h)))
                
                all_hands_landmarks.append(hand_info)
                
                if draw:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        return frame, all_hands_landmarks