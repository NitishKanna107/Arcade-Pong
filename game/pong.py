# Written by Nitish Kanna
# 22/06/2024, India
# Version 0.0.1

import cv2
import numpy as np
import mediapipe as mp

import traceback
import gesture
import random

class Game:
    version = '0.0.1'

    cam = None
    capWidth = 0
    capHeight = 0

    # event codes
    EVT_ONE_PLAYER = 1
    EVT_TWO_PLAYER = 2
    EVT_QUIT_GAME = -1

    def __init__(self, camID, capWidth, capHeight, sceneW, sceneH):
        Game.capWidth, Game.capHeight = capWidth, capHeight # webcam capture screen's dimensions
        # webcam faster launch and setup
        Game.cam = cv2.VideoCapture(camID, cv2.CAP_DSHOW)
        Game.cam.set(cv2.CAP_PROP_FRAME_WIDTH, Game.capWidth)
        Game.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, Game.capHeight)
        Game.cam.set(cv2.CAP_PROP_FPS, 30)
        Game.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        Game.render = Draw(sceneW, sceneH, scene = 'Arcade-Pong', capture = 'Finger Tracker')
    
    def start(self):
        Game.buttons = Game.render.menu() # returns a dictionary containing button labels as keys and button coordinates as values
        Game.caught_evt = None

        cv2.namedWindow(Game.render.scene)
        cv2.setMouseCallback(Game.render.scene, Game.events)
        
        while Game.caught_evt == None: # wait until user clicks play
            Game.render.draw()
        return Game.caught_evt
    
    def events(event, xpos, ypos, flags, params):
        # Game.buttons is a list of buttons created. Each button
        # is a list containing two tuples with the x and y coordinates 
        # of the upper left and lower right points of button box. 
        if event == cv2.EVENT_LBUTTONDOWN:
            buttonPlay1 = Game.buttons[0]
            buttonPlay2 = Game.buttons[1]
            buttonQuit = Game.buttons[2]

            # on mouse click check if mouse pointer is within the button box's area
            if ypos >= buttonPlay1[0][1] and ypos <= buttonPlay1[1][1]:
                if xpos >= buttonPlay1[0][0] and xpos <= buttonPlay1[1][0]:
                    Game.caught_evt = Game.EVT_ONE_PLAYER
            elif ypos >= buttonQuit[0][1] and ypos <= buttonQuit[1][1]:
                if xpos >= buttonQuit[0][0] and xpos <= buttonQuit[1][0]:
                    Game.caught_evt = Game.EVT_QUIT_GAME
            elif ypos >= buttonPlay2[0][1] and ypos <= buttonPlay2[1][1]:
                if xpos >= buttonPlay2[0][0] and xpos <= buttonPlay2[1][0]:
                    Game.caught_evt = Game.EVT_TWO_PLAYER
        # In the future, these buttons will be implemented using a 
        # proper GUI framework like Qt.
                
    def single_player():
        padObj = Paddle(100, 30, (255, 255, 255), 1)
        ballObj = Ball(Game.render.midpoint, 15, (0, 0, 255), 13, 12)

        hands = mp.solutions.hands.Hands(False, 1, 1, .5, .5) 
        playObj = Player(gesture.index, hands)
        key_evt = -1

        while key_evt & 0xFF != ord('b'): # press 'b' to return to main menu
            ret, frame = Game.cam.read()
            key_evt = Game.render.draw()

            if playObj.lives == 0:
                Game.render.over()
                continue

            ballObj.move()
            paddle_pos = playObj.position(frame)
            padObj.move(paddle_pos)

            collides = Game.collision(padObj, ballObj)

            if collides == True:
                playObj.score += 1
                ballObj.speedy *= -1 # reverse the vertical direction of the ball
            elif collides == False:
                playObj.lives -= 1
                newSpawn = Game.render.sceneW // 2, Game.render.sceneH - ballObj.radius # respawn point is at the bottom of the screen
                ballObj.location = list(newSpawn)

            Game.render.clear()
            Game.render.paddle(padObj)
            Game.render.ball(ballObj)
            Game.render.stats(playObj)
            cv2.imshow('Capture', frame)
            cv2.moveWindow('Capture', Game.render.sceneW, 0)

        cv2.destroyWindow('Capture')
        Game.cam.release()
        Game.render.clear()

    def collision(padObj, ballObj):
        # check if ball collides with the paddle
        if (ballObj.location[1] - ballObj.radius) <= padObj.lowerR[1]:
            if (ballObj.location[0] >= padObj.upperL[0]) and (ballObj.location[0] <= padObj.lowerR[0]):
                return True
            else:
                return False

class Draw:
    head_font = cv2.FONT_HERSHEY_COMPLEX
    subhead_font = cv2.FONT_HERSHEY_PLAIN

    head_color = (255, 255, 255)
    subhead_color = (140, 140, 140)
    button_color = (214, 214, 214)

    def __init__(self, sceneW, sceneH, scene, capture):
        self.sceneW = sceneW
        self.sceneH = sceneH
        self.midpoint = sceneW // 2, sceneH // 2

        self.scene = scene # game window title
        self.capture = capture

        self.gameFrame = np.zeros((sceneH, sceneW, 3), dtype = np.uint8)

    def menu(self):
        # Text coordinates
        title = self.midpoint[0] - 230, 70
        playOne = self.midpoint[0] - 100, title[1] + 90
        playTwo = playOne[0], playOne[1] + 70
        quitGame = playTwo[0] + 60, playTwo[1] + 70
        version = 30, 500

        cv2.putText(self.gameFrame, self.scene, title, Draw.head_font, 2, Draw.head_color, 2)
        cv2.putText(self.gameFrame, 'ONE-PLAYER', playOne, Draw.subhead_font, 2, Draw.subhead_color, 2)
        cv2.putText(self.gameFrame, 'TWO-PLAYER', playTwo, Draw.subhead_font, 2, Draw.subhead_color, 2)
        cv2.putText(self.gameFrame, 'QUIT', quitGame, Draw.subhead_font, 2, Draw.subhead_color, 2)
        cv2.putText(self.gameFrame, f'version {Game.version}', version, Draw.subhead_font, 1.3, Draw.head_color, 1)

        buttonPlay1 = [(playOne[0] - 10, playOne[1] - 30), (playOne[0] + 215, playOne[1] + 10)]
        buttonPlay2 = [(playTwo[0] - 10, playTwo[1] - 30), (playTwo[0] + 215, playTwo[1] + 10)]
        buttonQuit = [(quitGame[0] - 10, quitGame[1] - 30), (quitGame[0] + 80, quitGame[1] + 10)]

        cv2.rectangle(self.gameFrame, buttonPlay1[0], buttonPlay1[1], Draw.button_color, 2)
        cv2.rectangle(self.gameFrame, buttonPlay2[0], buttonPlay2[1], Draw.button_color, 2)
        cv2.rectangle(self.gameFrame, buttonQuit[0], buttonQuit[1], Draw.button_color, 2)

        return buttonPlay1, buttonPlay2, buttonQuit
    
    def over(self):
        tagLoc = (self.sceneW // 2 - 150, self.sceneH // 2)
        quitLoc = (tagLoc[0] + 10, tagLoc[1] + 50)
        cv2.putText(self.gameFrame, 'Game Over!', tagLoc, self.head_font, 1.5, self.head_color, 2)
        cv2.putText(self.gameFrame, 'Main Menu - [b]', quitLoc, self.subhead_font, 2, self.subhead_color, 2)

    def paddle(self, padObj):
        cv2.rectangle(self.gameFrame, padObj.upperL, padObj.lowerR, padObj.color, -1)
    
    def ball(self, ballObj):
        cv2.circle(self.gameFrame, ballObj.location, ballObj.radius, ballObj.color, -1)
    
    def stats(self, playObj):
        scoreLoc = 5, self.sceneH - 50
        livesLoc = 5, self.sceneH - 5
        cv2.putText(self.gameFrame, f'Score: {playObj.score}', scoreLoc, self.head_font, 1.2, self.head_color, 2)
        cv2.putText(self.gameFrame, f'Lives: {playObj.lives}', livesLoc, self.head_font, 1.2, self.head_color, 2)

    def draw(self):
        cv2.imshow(self.scene, self.gameFrame)
        cv2.moveWindow(self.scene, 0, 0)
        return cv2.waitKey(1) # necessary after cv2.imshow()
    
    def clear(self):
        self.gameFrame[:] = 0

class Player:
    def __init__(self, finger, hands):
        self.lives = 3
        self.score = 0

        self.finger = finger # finger to track for input
        self.hands = hands
        # only the x coordinate of the finger's position will be needed.
        # initially, the finger position will be taken to be at the middle of the screen.
        self.location = Game.render.midpoint[0]
    
    def position(self, frame):
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)
        if results.multi_hand_landmarks != None:
            playerHand = gesture.Hand(results, Game.capWidth, Game.capHeight)
            playerHand.markup(frame, self.finger)
            fingerMark = playerHand.finger(self.finger, playerHand.hands[0]) # landmarks of the finger
            # x coordinate of the tip of the finger being tracked is relative to 
            # the capture window's dimensions. Hence, it needs to be mapped to be relative
            # to the game window's dimensions.
            self.location = int((fingerMark[3][0] / Game.capWidth) * Game.render.sceneW)
            # mirror the movement as the webcam feed is not mirrored (right is left and left is right).
            self.location = Game.render.sceneW - self.location
        return self.location

class Paddle:
    def __init__(self, width, height, color, place):
        self.width = width
        self.height = height
        self.color = color
        self.place = place 
    
    def move(self, point):
        # move the middle of the paddle to where point is
        self.midpoint = point
        # set upper left point's coordinates
        xpos = self.midpoint - (self.width // 2)
        ypos = 0 # to be changed later as it must consider self.place
        self.upperL = xpos, ypos
        # set lower right point's coordinates
        xpos = self.midpoint + (self.width // 2)
        ypos = self.height
        self.lowerR = xpos, ypos

class Ball:
    def __init__(self, spawnLoc, radius, color, max_speed, min_speed):
        self.location = list(spawnLoc) # tuple to list as location will keep changing
        self.radius = radius
        self.color = color

        self.speedx = 5 # initial speed in the horizontal direction
        self.speedy = 3 # initial speed in the vertical direction
        self.max_speed = max_speed
        self.min_speed = min_speed
    
    def move(self):
        # check if ball touches any of the four walls
        if self.location[0] <= self.radius: # bounce off of the left wall
            self.speedx = random.randint(self.min_speed, self.max_speed)
        elif self.location[0] >= (Game.render.sceneW - self.radius): # bounce off of the right wall
            self.speedx = random.randint(self.min_speed, self.max_speed) * -1
        
        if self.location[1] >= (Game.render.sceneH - self.radius): # bounce off of the bottom wall
            self.speedy = random.randint(self.min_speed, self.max_speed) * -1
        
        self.location[0] += self.speedx
        self.location[1] += self.speedy

try:
    # the first argument of the Game class constructor is the camera ID. 
    # 0 should work for most cameras but if OpenCV doesn't detect
    # your camera then experiment with other numbers (1, 2, 3, ...).
    pong = Game(0, 640, 480, 858, 525)

    while True:
        playMode = pong.start()
        if playMode == Game.EVT_ONE_PLAYER:
            Game.single_player()
        elif playMode == Game.EVT_TWO_PLAYER:
            print('TWO PLAYER')
        elif playMode == Game.EVT_QUIT_GAME:
            break
except Exception:
    print(traceback.format_exc())