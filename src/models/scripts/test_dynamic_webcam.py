import cv2
import os
import joblib
import numpy as np
import collections
import mediapipe as mp

# Configuration
script_dir = os.path.dirname(os.path.abspath(__file__))
DYNAMIC_MODEL_PATH = os.path.join(script_dir, "..", "saved_models", "dynamic_asl_model.pkl")

SEQUENCE_LENGTH = 45  # 1.5 seconds @ 30 FPS

# Threshold Parameters (Tune these if needed)
MOTION_THRESHOLD = 0.012  # Minimum wrist movement (std dev) required to trigger gesture detection
CONFIDENCE_THRESHOLD = 75.0  # Minimum % confidence required to accept a prediction


def main():
    if not os.path.exists(DYNAMIC_MODEL_PATH):
        print(f"Error: Dynamic model not found at {DYNAMIC_MODEL_PATH}")
        return

    print("Loading Tier 2 Dynamic Model...")
    dynamic_model = joblib.load(DYNAMIC_MODEL_PATH)
    print("Model loaded successfully!\n")

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3
    )
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    frame_buffer = collections.deque(maxlen=SEQUENCE_LENGTH)
    raw_landmarks_buffer = collections.deque(maxlen=SEQUENCE_LENGTH)
    last_valid_normalized = None
    last_valid_raw = None

    print("--- Tier 2 Dynamic Test Bench (Filtered) ---")
    print(f"Motion Threshold: {MOTION_THRESHOLD} | Confidence Threshold: {CONFIDENCE_THRESHOLD}%")
    print("Perform J, Z, or 10 in front of the camera.")
    print("Press 'q' to quit\n")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 1. Store raw wrist coordinates for motion tracking (un-normalized)
            wrist_raw = (hand_landmarks.landmark[0].x, hand_landmarks.landmark[0].y)
            raw_landmarks_buffer.append(wrist_raw)
            last_valid_raw = wrist_raw

            # 2. Extract wrist-relative landmarks for model input
            wrist = hand_landmarks.landmark[0]
            normalized = []
            for lm in hand_landmarks.landmark:
                normalized.extend([lm.x - wrist.x, lm.y - wrist.y])

            last_valid_normalized = normalized
            frame_buffer.append(normalized)

        elif len(frame_buffer) > 0 and last_valid_normalized is not None:
            # Pad brief tracking flickers
            frame_buffer.append(last_valid_normalized)
            raw_landmarks_buffer.append(last_valid_raw)

        # --- Inference & Filtering Pipeline ---
        if len(frame_buffer) == SEQUENCE_LENGTH:
            # Calculate wrist position standard deviation over the sequence
            wrist_x = [pt[0] for pt in raw_landmarks_buffer]
            wrist_y = [pt[1] for pt in raw_landmarks_buffer]
            motion_score = np.std(wrist_x) + np.std(wrist_y)

            # METHOD 2: Motion Gate
            if motion_score < MOTION_THRESHOLD:
                display_text = "IDLE (Hand Stationary)"
                text_color = (200, 200, 200)
            else:
                # Run Model Prediction
                flattened_seq = np.array(frame_buffer).flatten().reshape(1, -1)
                prediction = dynamic_model.predict(flattened_seq)[0]

                if hasattr(dynamic_model, "predict_proba"):
                    probs = dynamic_model.predict_proba(flattened_seq)
                    confidence = np.max(probs) * 100

                    # METHOD 3: Confidence Gate
                    if confidence < CONFIDENCE_THRESHOLD:
                        display_text = f"NO GESTURE ({confidence:.1f}%)"
                        text_color = (0, 165, 255)
                    else:
                        display_text = f"GESTURE: {prediction} ({confidence:.1f}%)"
                        text_color = (0, 255, 0)
                else:
                    display_text = f"GESTURE: {prediction}"
                    text_color = (0, 255, 0)
        else:
            display_text = f"BUFFERING... ({len(frame_buffer)}/{SEQUENCE_LENGTH})"
            text_color = (255, 255, 255)

        # Banner Overlay
        cv2.rectangle(frame, (0, 0), (640, 60), (30, 30, 30), -1)
        cv2.putText(
            frame, 
            display_text, 
            (10, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.8, 
            text_color, 
            2
        )

        cv2.imshow("FingerLingo - Dynamic Test Bench", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()


if __name__ == "__main__":
    main()