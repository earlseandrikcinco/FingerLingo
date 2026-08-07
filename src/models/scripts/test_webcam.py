import cv2
import sys
import os

# Get absolute path to the directory containing test_webcam.py (src/models/scripts)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go UP TWO LEVELS: src/models/scripts -> src/models -> src
src_dir = os.path.abspath(os.path.join(script_dir, "..", ".."))

# Add 'src' to Python's module search path BEFORE importing 'models'
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Now Python can find 'models.hand_detector'

from models.hand_detector import HandDetector

def main():
    detector = HandDetector()

    cap = cv2.VideoCapture(0)
    print("\n--- Mode Controls ---")
    print("Press '1': LETTERS MODE (A-Y)")
    print("Press '2': NUMBERS MODE (1-9)")
    print("Press '3': LESSON A-E MODE")
    print("Press '0': ALL CLASSES (Unfiltered)")
    print("Press 'q': Exit")

    # Define filter presets
    PRESETS = {
        '1': [chr(i) for i in range(ord('A'), ord('Z')+1) if chr(i) not in ['J', 'Z']],
        '2': [str(i) for i in range(0, 10)],
        '3': ['A', 'B', 'C', 'D', 'E'],
        '0': None
    }

    current_mode_key = '0'
    mode_names = {
        '1': "Letters (A-Y)",
        '2': "Numbers (1-9)",
        '3': "Lesson A-E",
        '0': "All Classes"
    }

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Get active class filter based on mode key
        active_filter = PRESETS.get(current_mode_key, None)
        prediction_text = detector.process_frame(frame, allowed_classes=active_filter)

        # Draw UI overlay
        cv2.putText(
            frame, 
            f"Mode: {mode_names[current_mode_key]} (Press 0/1/2/3)", 
            (10, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (255, 255, 0), 
            2
        )
        cv2.putText(
            frame, 
            f"Sign: {prediction_text}", 
            (10, 90), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.2, 
            (0, 255, 0), 
            3
        )

        cv2.imshow("ASL Tier 1 Context Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif chr(key) in PRESETS:
            current_mode_key = chr(key)
            print(f"Switched to Mode: {mode_names[current_mode_key]}")

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    main()