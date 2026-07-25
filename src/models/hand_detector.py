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


        fingers = [] # This holds the list of booleans in this order [Thumb, Index, Middle, Ring, Pinky]

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            h, w, c = frame.shape # Height, width, and channels of the frame

            #THE WRIST
            wrist = (hand.landmark[0].x, hand.landmark[0].y)

           
            """
            For the thumb, since it goes across the palm, we need to compare the distance from the thumb tip 
            to the pinky knuckle with the distance from the index knuckle to the pinky knuckle. If the thumb 
            tip is further away than the distance between the index and pinky knuckles, then we can say that the thumb is raised.
            (This is also why I already defined the index and pink knuckles, since we need them for the thumb check)

            """
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

            """
            The rest of the fingers, will be checked by comparing the distance from the tip of the finger 
            to the wrist with the distance from the knuckle of the finger to the wrist.
            """
            
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


        return fingers #we finally return the list of booleans, which will be used to determine the sign being made by the hand


    def get_sign_label(self, fingers):
        #where the sign languages (albeit for now only static ones) are defined, based on the list of booleans that is returned by the get_raised_fingers function

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
        """ This is the buffer method that will help to stabilize the sign detection 
        by keeping a history of the last few detected signs and returning the most common one."""

        raw_sign = self.get_sign_label(fingers)

        self.prediction_history.append(raw_sign) # self.prediction_history is a deque that stores the last 15 (defined in the __init__ method) detected signs

        return statistics.mode(self.prediction_history)  # Return the most common sign in the history
    
