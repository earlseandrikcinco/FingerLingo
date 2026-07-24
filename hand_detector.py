import cv2
import mediapipe as mp

#used for better accuracy in detecting the hand and its landmarks
import math 

#for buffer purposes
from collections import deque
import statistics


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

        self.prediction_history = deque(maxlen=15)  # Store the last 15 predictions for smoothing

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

            #DA WRIST
            wrist = (hand.landmark[0].x, hand.landmark[0].y)

            #pinky and knuckle base (the reason why its here its because we need this also for the thumb
            index_knuckle = (hand.landmark[6].x, hand.landmark[6].y)
            pinky_knuckle = (hand.landmark[18].x, hand.landmark[18].y) 

            #THUMB
            thumb_tip = (hand.landmark[4].x, hand.landmark[4].y)

            thumb_to_pinky_dist = math.dist(thumb_tip, pinky_knuckle)

            palm_width_dist = math.dist(index_knuckle, pinky_knuckle)

            if thumb_to_pinky_dist > palm_width_dist:
                fingers.append(True)
            else:
                fingers.append(False)

            #INDEX FINGER
            index_tip = (hand.landmark[8].x, hand.landmark[8].y)
       

            index_tip_dist = math.dist(wrist, index_tip)
            index_knuckle_dist = math.dist(wrist, index_knuckle)


            if index_tip_dist > index_knuckle_dist:
                fingers.append(True)
            else:
                fingers.append(False)

            #MIDDLE FINGER
            middle_tip = (hand.landmark[12].x, hand.landmark[12].y)
            middle_knuckle = (hand.landmark[10].x, hand.landmark[10].y)

            middle_tip_dist = math.dist(wrist, middle_tip)
            middle_knuckle_dist = math.dist(wrist, middle_knuckle)

            if middle_tip_dist > middle_knuckle_dist:
                fingers.append(True)
            else:
                fingers.append(False)


            #RING FINGER
            ring_tip = (hand.landmark[16].x, hand.landmark[16].y)
            ring_knuckle = (hand.landmark[14].x, hand.landmark[14].y)

            ring_tip_dist = math.dist(wrist, ring_tip)
            ring_knuckle_dist = math.dist(wrist, ring_knuckle)

            if ring_tip_dist > ring_knuckle_dist:
                fingers.append(True)
            else:
                fingers.append(False)    

            #PINKY FINGER
            pinky_tip = (hand.landmark[20].x, hand.landmark[20].y)
            

            pinky_tip_dist = math.dist(wrist, pinky_tip)
            pinky_knuckle_dist = math.dist(wrist, pinky_knuckle)

            if pinky_tip_dist > pinky_knuckle_dist:
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
        elif fingers == [True, False, False, False, False]:
            return "Thumbs Up"
        elif fingers == [False, False, False, False, False]:
            return "Closed Hand"
        elif fingers == [True, True, True, True, True]:
            return "Open Hand"
        else:
            return "Unknown sign"

    def get_stable_sign_label(self, fingers):
        raw_sign = self.get_sign_label(fingers)

        self.prediction_history.append(raw_sign)

        return statistics.mode(self.prediction_history)  # Return the most common sign in the history
    
