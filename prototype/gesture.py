# Written by Nitish Kanna
# 20/06/2024, India

# Data type for storing and accessing Mediapipe Hand Landmark data in the most
# convenient way.

import cv2

# finger codes representing the ending index in the landmarks list
wrist = 1
thumb = 5
index = 9
middle = 13
ring = 17
pinky = 21

__version__ = '0.0.1'

class Hand:
    # hand_data stores the multi_hand_landmarks object returned by hands.process() method
    # width and height correspond to the display frame's dimensions
    def __init__(self, hand_data, width, height): 
        self.hands = []

        for hand in hand_data:
           landmarks = []

           for landmark in hand.landmark:
               xpos = int(landmark.x * width)
               ypos = int(landmark.y * height)
               landmarks.append((xpos, ypos)) 
           self.hands.append(landmarks)

    # method for extracting a finger's landmarks
    def finger(self, fcode, hand):
        if fcode == wrist:
            return [hand[0]]
        
        landmarks = []
        for i in range(fcode - 4, fcode): # each finger has four landmarks
            landmarks.append(hand[i])
        return landmarks

    # returns a dictionary with fingers as keys and landmarks as values
    def finger_dict(landmarks):
        finger_names = [
            "thumb",
            "index",
            "middle",
            "ring",
            "pinky"
        ]

        i = 1
        fingers = dict()
        for finger in finger_names:
            finger_marks = []
            for j in range(4):
                finger_marks.append(landmarks[i])
                i += 1
            fingers[finger] = finger_marks

        fingers['wrist'] = [landmarks[0]]
        return fingers

    # method for marking the landmarks of a hand with red spots
    def markup(self, frame, fcode = -1, max_hands = -1):
        if max_hands == -1: # mark all hands
                max_hands = len(self.hands)
        drawn = 0 # number of hands marked

        for hand in self.hands:
            if drawn == max_hands:
                continue

            landmarks = []
            if fcode == -1: # mark all fingers
                landmarks = hand
            else:
                landmarks = Hand.finger(self, fcode, hand)
            
            for landmark in landmarks:
                cv2.circle(frame, landmark, 4, (150, 150, 150), 2)
                cv2.circle(frame, landmark, 3, (0, 0, 255), -1)
            drawn += 1

    # method for displaying the HandMarks data structure
    def struct(self):
        for i in range(len(self.hands)): 
            print(f'{i}. Hand [') # prints the hand number
            fingers = Hand.finger_dict(self.hands[i])

            for finger, fingermarks in fingers.items(): # prints the landmark data for each finger
                print(f'\t{finger}', '{')

                for fingermark in fingermarks:
                    print(f'\t\t{fingermark}')

                print('\t}')
            print(']', '\n')
