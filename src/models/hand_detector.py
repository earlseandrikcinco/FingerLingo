import os
import joblib
import cv2
import numpy as np
import mediapipe as mp


class HandDetector:
    def __init__(self, model_dir=None):
        if model_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(script_dir, "saved_models")

        model_path = os.path.join(model_dir, "asl_model.pkl")
        encoder_path = os.path.join(model_dir, "label_encoder.pkl")

        print("Loading Tier 1 Random Forest model...")
        self.model = joblib.load(model_path)
        self.label_encoder = joblib.load(encoder_path)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame, allowed_classes=None):
        """
        Processes a single frame. If allowed_classes is provided (e.g. ['A', 'B', 'C']),
        the model only considers predictions within that allowed list.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return "No Hand Detected"

        hand_landmarks = results.multi_hand_landmarks[0]
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        # Extract normalized landmarks
        wrist = hand_landmarks.landmark[0]
        normalized_landmarks = []
        for landmark in hand_landmarks.landmark:
            nx = landmark.x - wrist.x
            ny = landmark.y - wrist.y
            normalized_landmarks.extend([nx, ny])

        features = np.array(normalized_landmarks).reshape(1, -1)

        # If no mode filter is provided, return standard top prediction
        if not allowed_classes:
            prediction_idx = self.model.predict(features)[0]
            return self.label_encoder.inverse_transform([prediction_idx])[0]

        # Context Filtering Mode: Filter probabilities for allowed classes only
        probabilities = self.model.predict_proba(features)[0]
        all_classes = self.label_encoder.classes_

        # Build dictionary of class -> probability for allowed classes
        filtered_probs = {
            cls_name: prob 
            for cls_name, prob in zip(all_classes, probabilities) 
            if cls_name in allowed_classes
        }

        if not filtered_probs:
            return "No Valid Target"

        # Return class with highest probability among allowed choices
        best_class = max(filtered_probs, key=filtered_probs.get)
        return best_class

    def close(self):
        self.hands.close()
