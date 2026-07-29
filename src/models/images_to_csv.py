import os
import cv2
import mediapipe as mp
import csv


def extract_dataset(dataset_path, output_csv):
    # 1. Initialize MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

    # 2. Set up the CSV file and headers
    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        header = ['label']
        for i in range(21):
            header.extend([f'x{i}', f'y{i}'])
        writer.writerow(header)

        success_count = 0
        fail_count = 0
        total_processed = 0  # Track total images looked at

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

                # SAFETY NET: Try-except block for corrupted files
                try:
                    image = cv2.imread(image_path)

                    if image is None:
                        continue

                    # Convert to RGB for MediaPipe
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    results = hands.process(rgb_image)

                    # 5. If a hand is found, normalize and save!
                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]

                        # Grab wrist coordinates for normalization
                        wrist_x = hand_landmarks.landmark[0].x
                        wrist_y = hand_landmarks.landmark[0].y

                        normalized_landmarks = []
                        for landmark in hand_landmarks.landmark:
                            nx = landmark.x - wrist_x
                            ny = landmark.y - wrist_y
                            normalized_landmarks.extend([nx, ny])

                        # Save the folder name as the label
                        writer.writerow([folder_name.upper()] + normalized_landmarks)
                        success_count += 1
                    else:
                        fail_count += 1

                except Exception as e:
                    print(f"Error processing {image_name}: {e}")
                    fail_count += 1
                    continue

                # PROGRESS TRACKER & DATA SAVER
                # Every 1,000 images, print an update and force-save the CSV to disk
                if total_processed % 1000 == 0:
                    print(f"    ...Processed {total_processed} images so far. (Found hands in {success_count})")
                    f.flush()

    print("-" * 30)
    print("Extraction Complete!")
    print(f"✅ Successfully extracted landmarks from {success_count} images.")
    print(f"❌ Failed to find hands in {fail_count} images.")

    # Clean up
    hands.close()


if __name__ == "__main__":
    # CHANGE THIS to the path where your dataset folders are!
    DATASET_DIRECTORY = "src/models/processed_combine_asl_dataset"
    OUTPUT_FILE = "extracted_asl_data.csv"

    extract_dataset(DATASET_DIRECTORY, OUTPUT_FILE)
