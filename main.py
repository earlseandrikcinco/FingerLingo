from camera import Camera
from hand_detector import HandDetector
import cv2

camera = Camera()

detector = HandDetector()

while True:

    frame = camera.get_frame()

    if frame is None:
        break

    results = detector.detect(frame)

    detector.draw(frame, results)


    fingers =  detector.get_raised_fingers(frame, results)

    sign = detector.get_sign_label(fingers)
    cv2.putText(frame, sign, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


    camera.show(frame)

    if camera.should_quit():
        break


detector.close()
camera.release()
