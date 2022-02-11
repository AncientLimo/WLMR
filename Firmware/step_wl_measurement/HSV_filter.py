import sys
import cv2
import numpy as np
import time


def add_HSV_filter(frame, camera):

	# Difumina los fotogramas recibidos 
    blur = cv2.GaussianBlur(frame,(5,5),0)

    # Convierte de RGB a HSV 
    frameHSV = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    redbot0 = np.array([0, 100, 20], np.uint8)
    redtop0 = np.array([8, 255, 255], np.uint8)
    redbot1 = np.array([170, 100, 20], np.uint8)
    redtop1 = np.array([179, 255, 255], np.uint8)

    maskred1 = cv2.inRange(frameHSV, redbot0, redtop0)
    maskred2 = cv2.inRange(frameHSV, redbot1, redtop1)
    maskred = cv2.add(maskred1, maskred2)


    # Operaciones morfológicas para reducir ruido
    maskred = cv2.erode(maskred, None, iterations=2)
    maskred = cv2.dilate(maskred, None, iterations=2)

    return maskred