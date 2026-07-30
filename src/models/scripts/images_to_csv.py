import os
import cv2
import mediapipe as mp
import csv


def extract_dataset(dataset_path, output_csv):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.1
    )

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        header = ['label']
        for i in range(21):
            header.extend([f'x{i}', f'y{i}'])
        writer.writerow(header)

        success_count = 0
        fail_count = 0
        total_processed = 0

        entries = os.listdir(dataset_path)
        subfolders = [e for e in entries if os.path.isdir(os.path.join(dataset_path, e))]

        if subfolders:
            print("Found subfolder structure...")
            for folder_name in sorted(subfolders):
                folder_path = os.path.join(dataset_path, folder_name)
                print(f"--> Starting folder: {folder_name}...")

                for image_name in os.listdir(folder_path):
                    if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        continue
                    
                    label = folder_name.upper()
                    image_path = os.path.join(folder_path, image_name)
                    success_count, fail_count, total_processed = process_image(
                        image_path, label, hands, writer, success_count, fail_count, total_processed, f
                    )
        else:
            print("Found direct loose images structure...")
            for image_name in sorted(entries):
                if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue

                label = image_name.split('_')[0].upper()
                image_path = os.path.join(dataset_path, image_name)
                success_count, fail_count, total_processed = process_image(
                    image_path, label, hands, writer, success_count, fail_count, total_processed, f
                )

    print("-" * 30)
    print("Extraction Complete!")
    print(f"✅ Successfully extracted landmarks from {success_count} images.")
    print(f"❌ Failed to find hands in {fail_count} images.")

    hands.close()


def process_image(image_path, label, hands, writer, success_count, fail_count, total_processed, f_handle):
    total_processed += 1
    try:
        image = cv2.imread(image_path)
        if image is None:
            return success_count, fail_count + 1, total_processed

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_image)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            wrist_x = hand_landmarks.landmark[0].x
            wrist_y = hand_landmarks.landmark[0].y

            normalized_landmarks = []
            for landmark in hand_landmarks.landmark:
                nx = landmark.x - wrist_x
                ny = landmark.y - wrist_y
                normalized_landmarks.extend([nx, ny])

            writer.writerow([label] + normalized_landmarks)
            success_count += 1
        else:
            fail_count += 1

    except Exception as e:
        print(f"Error processing {os.path.basename(image_path)}: {e}")
        fail_count += 1

    if total_processed % 500 == 0:
        print(f"    ...Processed {total_processed} images so far. (Found hands in {success_count})")
        f_handle.flush()

    return success_count, fail_count, total_processed


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    DATASET_DIRECTORY = os.path.join(script_dir, "..", "data", "asl_alphabet_test")
    OUTPUT_FILE = os.path.join(script_dir, "..", "data", "test_asl_data.csv")

    extract_dataset(DATASET_DIRECTORY, OUTPUT_FILE)