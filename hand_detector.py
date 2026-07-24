import cv2
import mediapipe as mp


class HandDetector:

    def __init__(self):

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.drawer = mp.solutions.drawing_utils

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)

        return results

    def draw(self, frame, results):

        if results.multi_hand_landmarks:

            for landmarks in results.multi_hand_landmarks:

                self.drawer.draw_landmarks(
                    frame,
                    landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

        return frame

    def close(self):
        self.hands.close()

    def get_raised_fingers(self, frame, results):

        fingers = []

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            h, w, c = frame.shape

            #THUMB
            thumb_tip_x = hand.landmark[4].x * w
            thumb_knuckle_x = hand.landmark[2].x * w

            if thumb_tip_x > thumb_knuckle_x:
                fingers.append(True)
            else:
                fingers.append(False)

            #INDEX FINGER
            index_tip_y = hand.landmark[8].y * h
            index_knuckle_y = hand.landmark[6].y * h

            if index_tip_y < index_knuckle_y:
                fingers.append(True)
            else:
                fingers.append(False)

            #MIDDLE FINGER
            middle_tip_y = hand.landmark[12].y * h
            middle_knuckle_y = hand.landmark[10].y * h

            if middle_tip_y < middle_knuckle_y:
                fingers.append(True)
            else:
                fingers.append(False)


            #RING FINGER
            ring_tip_y = hand.landmark[16].y * h
            ring_knuckle_y = hand.landmark[14].y * h

            if ring_tip_y < ring_knuckle_y:
                fingers.append(True)
            else:
                fingers.append(False)    

            #PINKY FINGER
            pinky_tip_y = hand.landmark[20].y * h
            pinky_knuckle_y = hand.landmark[18].y * h

            if pinky_tip_y < pinky_knuckle_y:
                fingers.append(True)
            else:
                fingers.append(False)


        return fingers    


    def get_sign_label(self, fingers):
        if not fingers:
            return "No hand detected" 
        # the list look like this [Thumb, Index, Middle, Ring, Pinky]
        if fingers == [False, True, False, False, False]:
            return "Letter D"
        elif fingers == [False, True, True, False, False]:
            return "Peace Sign"
        elif fingers == [True, True, False, False, False]:
            return "Letter L"
        elif fingers == [False, False, True, False, False]:
            return "Fuck You"
        elif fingers == [False, False, False, False, False]:
            return "Closed Hand"
        elif fingers == [True, True, True, True, True]:
            return "Open Hand"
        else:
            return "Unknown sign"
        
