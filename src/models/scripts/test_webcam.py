import cv2
import os
import sys

# Ensure Python can find hand_detector.py in src/models/
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.abspath(os.path.join(script_dir, ".."))
if models_dir not in sys.path:
    sys.path.append(models_dir)

from hand_detector import HandDetector


def main():
    detector = HandDetector()

    cap = cv2.VideoCapture(0)
    print("Opening webcam... Press 'q' to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Delegate processing to Tier 1 detector
        prediction_text = detector.process_frame(frame)

        # Display result on screen
        cv2.putText(
            frame, 
            f"Sign: {prediction_text}", 
            (10, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.2, 
            (0, 255, 0), 
            3
        )

        cv2.imshow("ASL Tier 1 Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    main()