import cv2
import os
import csv
import numpy as np
import mediapipe as mp

# Configuration: Increased to 45 frames (1.5 seconds @ 30fps)
SEQUENCE_LENGTH = 45  
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(script_dir, "..", "data", "dynamic_asl_dataset.csv")


def init_csv(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not os.path.exists(output_path):
        with open(output_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            # Header: label + 1890 features (45 frames * 42 landmarks)
            header = ['label']
            for frame_idx in range(SEQUENCE_LENGTH):
                for lm_idx in range(21):
                    header.extend([f'f{frame_idx}_x{lm_idx}', f'f{frame_idx}_y{lm_idx}'])
            writer.writerow(header)


def main():
    init_csv(OUTPUT_CSV)

    mp_hands = mp.solutions.hands
    # Lower confidence thresholds to maintain tracking during fast motion
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.3
    )
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    print("\n--- Dynamic Data Collector (1.5s / 45 Frames) ---")
    print("Press 'j' -> Record J")
    print("Press 'z' -> Record Z")
    print("Press '1' -> Record 10")
    print("Press 'q' -> Quit\n")

    recording = False
    current_label = ""
    frame_buffer = []
    last_valid_normalized = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if recording:
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                wrist = hand_landmarks.landmark[0]
                normalized = []
                for lm in hand_landmarks.landmark:
                    normalized.extend([lm.x - wrist.x, lm.y - wrist.y])
                
                last_valid_normalized = normalized
                frame_buffer.append(normalized)

            elif last_valid_normalized is not None:
                # If tracking briefly drops mid-motion, duplicate the last frame to prevent gap
                frame_buffer.append(last_valid_normalized)

            # Draw progress bar
            progress = len(frame_buffer) / SEQUENCE_LENGTH
            cv2.rectangle(frame, (50, 400), (50 + int(progress * 300), 420), (0, 0, 255), -1)
            cv2.putText(
                frame, 
                f"RECORDING {current_label}: {len(frame_buffer)}/{SEQUENCE_LENGTH}", 
                (50, 390), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (0, 0, 255), 
                2
            )

            # Save sequence when buffer fills
            if len(frame_buffer) == SEQUENCE_LENGTH:
                flattened_sequence = [item for frame_lm in frame_buffer for item in frame_lm]
                with open(OUTPUT_CSV, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([current_label] + flattened_sequence)
                
                print(f"✅ Saved 1 sequence for '{current_label}'")
                recording = False
                frame_buffer = []
                last_valid_normalized = None

        else:
            if results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)

            cv2.putText(
                frame, 
                "Ready. Press 'j', 'z', or '1' (for 10)", 
                (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (255, 255, 0), 
                2
            )

        cv2.imshow("Dynamic Sequence Recorder", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif not recording:
            if key in [ord('j'), ord('z'), ord('1')]:
                current_label = 'J' if key == ord('j') else ('Z' if key == ord('z') else '10')
                recording = True
                frame_buffer = []
                last_valid_normalized = None

    cap.release()
    cv2.destroyAllWindows()
    hands.close()


if __name__ == "__main__":
    main()