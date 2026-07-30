import os
import cv2
import mediapipe as mp
import csv


def extract_dataset(dataset_path, output_csv):
    # 1. Initialize MediaPipe (Standard confidence for real photos)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.5
    )

    # 2. Set up the CSV file and headers
    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        header = ['label']
        for i in range(21):
            header.extend([f'x{i}', f'y{i}'])
        writer.writerow(header)

        success_count = 0
        fail_count = 0
        total_processed = 0

        # 3. Loop through every folder
        for folder_name in sorted(os.listdir(dataset_path)):
            folder_path = os.path.join(dataset_path, folder_name)

            if not os.path.isdir(folder_path):
                continue

            print(f"--> Starting folder: {folder_name}...")

            # 4. Loop through every image
            for image_name in os.listdir(folder_path):
                if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue

                total_processed += 1
                image_path = os.path.join(folder_path, image_name)

                try:
                    image = cv2.imread(image_path)

                    if image is None:
                        continue

                    # Convert to RGB for MediaPipe (No padding needed for real photos!)
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = hands.process(rgb_image)

                    # 5. If a hand is found, normalize and save
                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]

                        wrist_x = hand_landmarks.landmark[0].x
                        wrist_y = hand_landmarks.landmark[0].y

                        normalized_landmarks = []
                        for landmark in hand_landmarks.landmark:
                            nx = landmark.x - wrist_x
                            ny = landmark.y - wrist_y
                            normalized_landmarks.extend([nx, ny])

                        # Save the folder name as the label ('A', 'DEL', 'SPACE')
                        writer.writerow([folder_name.upper()] + normalized_landmarks)
                        success_count += 1
                    else:
                        fail_count += 1

                except Exception as e:
                    print(f"Error processing {image_name}: {e}")
                    fail_count += 1
                    continue

                # Print progress every 5,000 images to avoid terminal spam
                if total_processed % 5000 == 0:
                    print(f"    ...Processed {total_processed} images so far. (Found hands in {success_count})")
                    f.flush()

    print("-" * 30)
    print("Extraction Complete!")
    print(f"✅ Successfully extracted landmarks from {success_count} images.")
    print(f"❌ Failed to find hands in {fail_count} images. (Expect many failures from the 'nothing' folder)")

    hands.close()


if __name__ == "__main__":
    # UPDATE THIS to your new ASL Alphabet train directory
    DATASET_DIRECTORY = "asl_alphabet_train"
    OUTPUT_FILE = "extracted_real_asl_data.csv"

    extract_dataset(DATASET_DIRECTORY, OUTPUT_FILE)
