import sys
import cv2
import numpy as np
import time
import imutils


def find_circles(frame, mask):

    points = []
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(contours)
    center = None

    if cnts:

        ordered = order_contours(cnts)

        if len(ordered) > 1:
            length = len(ordered)
            obj1, obj2 = (ordered[0], ordered[1])
            areaObj1, xObj1, yObj1 = (obj1[0], obj1[1], obj1[2])
            areaObj2, xObj2, yObj2 = (obj2[0], obj2[1], obj2[2])
            # cv2.drawContours(image, [newContour1], 0, (255, 0, 0), 3)
            # cv2.drawContours(image, [newContour2], 0, (255, 0, 0), 3)

            cv2.circle(frame, (xObj1, yObj1), 5, (0, 0, 0), -1)
            cv2.circle(frame, (xObj2, yObj2), 5, (0, 0, 0), -1)
            cv2.putText(frame, "TRACKING:" + str(length), (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124, 252, 0), 2)

            if xObj1 < xObj2:
                centerL = [(xObj1, yObj1)]
                centerR = [(xObj2, yObj2)]
            else:
                centerL = [(xObj2, yObj2)]
                centerR = [(xObj1, yObj1)]

            points = centerL + centerR

            return points


def order_contours(contours):

    data_global = []

    for c in contours:

        area = cv2.contourArea(c)

        if area > 500:
            M = cv2.moments(c)  # Cálculo de momentos
            (X, Y) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            data = [(area, X, Y)]     # Inserta área y coordenadas de cada contorno detectado en una lista 
            data_global = data_global + data  # Construye una tupla con los datos anteriormente almacenados para cada contorno


    # Ordena y regresa los datos ordenados de mayor a menor área de contorno
    data_ordered = sorted(data_global, reverse=True, key=lambda ar: ar[0]) 


    return data_ordered
