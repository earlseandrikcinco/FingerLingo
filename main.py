from camera import Camera
from hand_detector import HandDetector

camera = Camera()

detector = HandDetector()

while True:

    frame = camera.get_frame()

    if frame is None:
        break

    results = detector.detect(frame)

    detector.draw(frame, results)

    camera.show(frame)

    if camera.should_quit():
        break

detector.close()
camera.release()
