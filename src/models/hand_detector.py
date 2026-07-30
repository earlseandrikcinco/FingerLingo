import os
import cv2
import joblib
import numpy as np
import mediapipe as mp


class HandDetector:
    def __init__(self):
        # MediaPipe initialization
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Load Tier 1 ML model & encoder from saved_models/
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, 'saved_models', 'asl_model.pkl')
        encoder_path = os.path.join(base_dir, 'saved_models', 'label_encoder.pkl')

        self.model = joblib.load(model_path)
        self.label_encoder = joblib.load(encoder_path)

    def process_frame(self, frame):
        """
        Processes a BGR frame: draws landmarks and returns the predicted Tier 1 static sign label.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        sign = "No Hand Detected"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 1. Draw landmarks on frame
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                # 2. Extract relative landmarks for ML
                wrist_x = hand_landmarks.landmark[0].x
                wrist_y = hand_landmarks.landmark[0].y

                normalized_landmarks = []
                for lm in hand_landmarks.landmark:
                    normalized_landmarks.extend([lm.x - wrist_x, lm.y - wrist_y])

                # 3. Predict static sign using Random Forest
                features = np.array([normalized_landmarks])
                pred_num = self.model.predict(features)[0]
                sign = self.label_encoder.inverse_transform([pred_num])[0]

        return sign

    def close(self):
        self.hands.close()