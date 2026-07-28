import cv2
import mediapipe as mp
import csv
import os

"""This is used for collecting initial x and y datas"""


def setup_csv(filename="asl_dataset.csv"):
    # If the file doesn't exist, create it and add the header row
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)

            header = ['label']
            for i in range(21):
                header.extend([f'x{i}', f'y{i}'])
            writer.writerow(header)


def main():
    filename = "asl_dataset.csv"
    setup_csv(filename)

    mp_hands = mp.solutions.hands
    # max_num_hands=1 ensures we only record one hand at a time for cleaner data
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    print("Camera on! Press letters (a-z) or numbers (0-9) to save a frame.")
    print("Press 'ESC' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip frame so it acts like a mirror
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Draw landmarks
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Show the frame
        cv2.imshow("Data Collection", frame)

        # Listens for keyboard presses
        key = cv2.waitKey(1) & 0xFF

        # If ESC is pressed, quit
        if key == 27:
            break

        # If the key is a letter or digit AND a hand is visible
        valid_key = (ord('a') <= key <= ord('z')) or (ord('0') <= key <= ord('9'))

        if valid_key and results.multi_hand_landmarks:
            label = chr(key).upper()

            # Grab sthe wrist coordinates (Landmark 0)
            wrist = hand_landmarks.landmark[0]
            wrist_x = wrist.x
            wrist_y = wrist.y

            # Normalize and flatten the coordinates
            normalized_landmarks = []
            for landmark in hand_landmarks.landmark:
                # Subtract wrist coordinates to make everything relative to the wrist
                nx = landmark.x - wrist_x
                ny = landmark.y - wrist_y
                normalized_landmarks.extend([nx, ny])

            # Append to the CSV
            with open(filename, mode='a', newline='') as f:
                writer = csv.writer(f)

                writer.writerow([label] + normalized_landmarks)

            print(f"✅ Saved frame for label: {label}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
