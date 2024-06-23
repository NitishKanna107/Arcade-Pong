import cv2
import numpy as np

while cv2.waitKey(1) != ord('q'):
    frame = np.zeros((525, 858, 3), dtype=np.uint8)
    title = [858 // 2 - 230, 70]
    player1 = [(858 // 2 - 100), title[1] + 90]
    player2 = [player1[0], player1[1] + 70]
    gamequit = [player2[0] + 60, player2[1] + 70]
    version = [30, 500]
    cv2.putText(frame, 'Arcade-Pong', title, cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 4)
    cv2.putText(frame, 'ONE-PLAYER', player1, cv2.FONT_HERSHEY_PLAIN, 2, (140, 140, 140), 2)
    cv2.putText(frame, 'TWO-PLAYER', player2, cv2.FONT_HERSHEY_PLAIN, 2, (140, 140, 140), 2)
    cv2.putText(frame, 'QUIT', gamequit, cv2.FONT_HERSHEY_PLAIN, 2, (140, 140, 140), 2)
    cv2.putText(frame, 'version 0.0.1', version, cv2.FONT_HERSHEY_PLAIN, 1.3, (255, 255, 255), 1)

    cv2.imshow('Capture', frame)
    cv2.moveWindow('Capture', 0, 0)