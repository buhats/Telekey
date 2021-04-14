#------------------------------------------------------------
# SEGMENT, RECOGNIZE and COUNT fingers from a video sequence
#------------------------------------------------------------

# organize imports
#imports for computer commands
from __future__ import division
import re
import sys
import pyautogui
import pynput
from pynput.mouse import Button, Controller
#imports for finger counting
import cv2
import imutils
import numpy as np
from sklearn.metrics import pairwise

class VideoStream(object):

    def __init__(self):
        self._bg = None

    #--------------------------------------------------
    # To find the running average over the background
    #--------------------------------------------------
    def run_avg(self, image, accumWeight):
        # initialize the background
        if self._bg is None:
            self._bg = image.copy().astype("float")
            return

        # compute weighted average, accumulate it and update the background
        cv2.accumulateWeighted(image, self._bg, accumWeight)

    #---------------------------------------------
    # To segment the region of hand in the image
    #---------------------------------------------
    def segment(self, image, threshold=35):
        # find the absolute difference between background and current frame
        diff = cv2.absdiff(self._bg.astype("uint8"), image)

        # threshold the diff image so that we get the foreground
        thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]

        # get the contours in the thresholded image
        (cnts, _) = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # return None, if no contours detected
        if len(cnts) == 0:
            return
        else:
            # based on contour area, get the maximum contour which is the hand
            segmented = max(cnts, key=cv2.contourArea)
            return (thresholded, segmented)

    #--------------------------------------------------------------
    # To count the number of fingers in the segmented hand region
    #--------------------------------------------------------------
    def count(self, thresholded, segmented):
        # find the convex hull of the segmented hand region
        chull = cv2.convexHull(segmented)

        # find the most extreme points in the convex hull
        extreme_top    = tuple(chull[chull[:, :, 1].argmin()][0])
        extreme_bottom = tuple(chull[chull[:, :, 1].argmax()][0])
        extreme_left   = tuple(chull[chull[:, :, 0].argmin()][0])
        extreme_right  = tuple(chull[chull[:, :, 0].argmax()][0])

        # find the center of the palm
        cX = int((extreme_left[0] + extreme_right[0]) / 2)
        cY = int((extreme_top[1] + extreme_bottom[1]) / 2)

        # find the maximum euclidean distance between the center of the palm
        # and the most extreme points of the convex hull
        distance = pairwise.euclidean_distances([(cX, cY)], Y=[extreme_left, extreme_right, extreme_top, extreme_bottom])[0]
        maximum_distance = distance[distance.argmax()]

        # calculate the radius of the circle with 80% of the max euclidean distance obtained
        radius = int(0.8 * maximum_distance)

        # find the circumference of the circle
        circumference = (2 * np.pi * radius)

        # take out the circular region of interest which has 
        # the palm and the fingers
        circular_roi = np.zeros(thresholded.shape[:2], dtype="uint8")
        
        # draw the circular ROI
        cv2.circle(circular_roi, (cX, cY), radius, 255, 1)

        # take bit-wise AND between thresholded hand using the circular ROI as the mask
        # which gives the cuts obtained using mask on the thresholded hand image
        circular_roi = cv2.bitwise_and(thresholded, thresholded, mask=circular_roi)

        # compute the contours in the circular ROI
        (cnts, _) = cv2.findContours(circular_roi.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # initalize the finger count
        count = 0

        # loop through the contours found
        for c in cnts:
            # compute the bounding box of the contour
            (x, y, w, h) = cv2.boundingRect(c)

            # increment the count of fingers only if -
            # 1. The contour region is not the wrist (bottom area)
            # 2. The number of points along the contour does not exceed
            #     25% of the circumference of the circular ROI
            if ((cY + (cY * 0.25)) > (y + h)) and ((circumference * 0.25) > c.shape[0]):
                count += 1

        return count

    #-------------------------------------------------------------------------
    # To perform the correct command depending on the number of fingers shown
    #-------------------------------------------------------------------------
    def doCommand(self, finger_count):
        mouse = Controller()
        if finger_count==1:
            print("Clicking..")
            mouse.click(Button.left, 1)
                    
        if finger_count==3:
            print("Right Clicking..")
            mouse.click(Button.right, 1)
        
        if finger_count==4:
            print("Double Clicking..")
            mouse.click(Button.left, 2)

        # while finger_count==2 && moving up:
        #     print("Scrolling up..")
        #     mouse.scroll(0, 15)

        # while finger_count==2 && moving down:
        #     print("Scrolling down..")
        #     mouse.scroll(0, -15)
