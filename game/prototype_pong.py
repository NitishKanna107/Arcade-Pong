# Written by Nitish Kanna
# 21/06/2024, India
# Prototype version

import cv2
import numpy as np
import mediapipe as mp
import gesture

import random
import math

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
print('Running OpenCV', cv2.__version__)
print('Running Mediapipe', mp.__version__)
print('Running Gesture', gesture.__version__)

width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print('Frame dimensions:', width, 'x', height, '\n')

gwidth = 858
gheight = 525

pad_left = 0, 0 # upper left corner of the paddle
pad_right = 0, 0 # lower right corner of the paddle
centerx = 50 # x coordinate of the center of the paddle

ball_x = int(width/2) # spawn point of the ball 
ball_y = int(height) - 15

min_speed, max_speed = 10, 11
move_x = random.randint(min_speed, max_speed) # speed of the ball chosen randomly
move_y = move_x * -1

points = 0
lives = 3

def update_pos():
    global move_x, move_y
    if ball_x <= 15:
        move_x = random.randint(min_speed, max_speed)
    elif ball_x >= (gwidth - 15):
        move_x = random.randint(min_speed, max_speed) * -1
    
    if ball_y <= 16:
        return False
    elif ball_y >= (gheight - 15):
        move_y = random.randint(min_speed, max_speed) * -1
    
    return True

def game_run(frame, gameFrame):
    global ball_x, ball_y, move_x, move_y
    global centerx, points, lives

    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frameRGB)

    if results.multi_hand_landmarks != None: 
        myHands = gesture.Hand(results, width, height)
        myHands.markup(frame, gesture.index)
        indexFinger = myHands.finger(gesture.index, myHands.hands[0]) # landmarks of the index finger
        centerx = (indexFinger[3][0] / width) * gwidth # x coordinate of the tip of the index finger mapped to game frame size
        centerx = gwidth - int(centerx)

    ball_x += move_x
    ball_y += move_y

    cv2.rectangle(gameFrame, (centerx - 50, 0), (centerx + 50, 30), (255, 255, 255), -1)
    cv2.circle(gameFrame, (ball_x, ball_y), 15, (0, 0, 255), -1)
    cv2.putText(gameFrame, f'Score: {points}', (5, gheight - 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (255, 255, 255), 2)
    cv2.putText(gameFrame, f'Lives: {lives}', (5, gheight - 5), cv2.FONT_HERSHEY_COMPLEX, 1.2, (255, 255, 255), 2)

    if ball_x >= (centerx - 55) and ball_x <= (centerx + 55):
        if ball_y >= 15 and ball_y <= 30:
            move_y = random.randint(min_speed, max_speed)
            points += 1

    if update_pos() == False:
        ball_x = gwidth//2 
        ball_y = gheight - 50
        lives -= 1

try:
    hands = mp.solutions.hands.Hands(False, 1, 1, .5, .5) 
    gameRunning = False

    while cv2.waitKey(1) & 0xFF != ord('q'):
        ret, frame = cam.read()
        gameFrame = np.zeros((gheight, gwidth, 3), dtype=np.uint8)
        
        if gameRunning == False:
            cv2.putText(gameFrame, "Press 's' to start", (gwidth // 2 - 300, gheight // 2), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 0, 0), 2)
            if cv2.waitKey(1) & 0xFF == ord('s'):
                gameRunning = True
        else:
            if lives != 0:
                game_run(frame, gameFrame)
            else:
                cv2.putText(gameFrame, 'Game Over!', (gwidth // 2 - 150, gheight // 2), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 2)

        
        cv2.imshow('Game', gameFrame)
        cv2.moveWindow('Game', 0, 0)
        
        cv2.imshow('Capture', frame)
        cv2.moveWindow('Capture', gwidth, 0)

    cam.release()
except Exception as error:
    print(error)