import cv2


class Camera:

    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise Exception("Could not open camera.")

    def get_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def show(self, frame):
        cv2.imshow("Hand Detection", frame)

    def should_quit(self):
        return cv2.waitKey(1) & 0xFF == ord('q')
