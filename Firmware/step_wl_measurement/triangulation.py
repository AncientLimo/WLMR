import sys
import cv2
import numpy as np
import cmath
import time


def find_depth(circle_right, circle_left, frame_right, frame_left, baseline, f, alpha):


    height_right, width_right, _ = frame_right.shape
    height_left, width_left, _ = frame_left.shape

    if width_right == width_left:
        f_pixel = (width_right * 0.5) / np.tan(alpha * 0.5 * np.pi/180)

    else:
        print('Left and right camera frames do not have the same pixel width')

    x_right = circle_right[0]
    x_left = circle_left[0]

    disparity = x_left-x_right      

   
    zDepth = baseline*f_pixel/disparity          

    zDepth= abs(zDepth)

    if zDepth < 60:
        zDepth = zDepth + 5
    elif 60 <= zDepth < 68:
        zDepth = zDepth + 2

    elif 68 <= zDepth < 86:
        zDepth = zDepth + 2

    elif 98 < zDepth < 101:
        zDepth = zDepth - 2
    elif 101 < zDepth:
        zDepth = zDepth - 4.2

    return round(zDepth, 2)

