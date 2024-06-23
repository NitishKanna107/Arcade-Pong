# Written by Nitish Kanna
# 22/06/2024, India
# Version 0.0.1

import cv2
import numpy as np
import mediapipe as mp

import gesture
import random
import time

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

        if Game.caught_evt == Game.EVT_ONE_PLAYER:
            print('ONE PLAYER')
        elif Game.caught_evt == Game.EVT_TWO_PLAYER:
            print('TWO PLAYER')
        elif Game.caught_evt == Game.EVT_QUIT_GAME:
            return False
    
    def events(event, xpos, ypos, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Game.buttons is a list of buttons created. Each button
            # is a list containing two tuples with the x and y coordinates 
            # of the upper left and lower right points of button box. 
            buttonPlay1 = Game.buttons[0]
            buttonPlay2 = Game.buttons[1]
            buttonQuit = Game.buttons[2]

            # In the future, these buttons will be implemented using a 
            # proper GUI framework like Qt.
            if ypos >= buttonPlay1[0][1] and ypos <= buttonPlay1[1][1]:
                if xpos >= buttonPlay1[0][0] and xpos <= buttonPlay1[1][0]:
                    Game.caught_evt = Game.EVT_ONE_PLAYER
            elif ypos >= buttonQuit[0][1] and ypos <= buttonQuit[1][1]:
                if xpos >= buttonQuit[0][0] and xpos <= buttonQuit[1][0]:
                    Game.caught_evt = Game.EVT_QUIT_GAME
            elif ypos >= buttonPlay2[0][1] and ypos <= buttonPlay2[1][1]:
                if xpos >= buttonPlay2[0][0] and xpos <= buttonPlay2[1][0]:
                    Game.caught_evt = Game.EVT_TWO_PLAYER

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

        self.scene = scene
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

    def draw(self):
        cv2.imshow(self.scene, self.gameFrame)
        cv2.moveWindow(self.scene, 0, 0)
        cv2.waitKey(1) # necessary to call after cv2.imshow()

try:
    pong = Game(0, 640, 480, 858, 525)
    while True:
        feed = pong.start()
        if feed == False:
            break

except Exception as error:
    print(error)