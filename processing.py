import logging
import sys
from tkinter import Tk, messagebox
import eel
import base64
import time
import os
import json
import cv2
import numpy as np
from camera import VideoCamera
import threading


class VideoProcessing:

  def __init__(self):    
    self.kernel = np.ones((8, 8), "uint8")
    self.capture = VideoCamera("./web/image/video/brick1_01")
    self.output = "Detection"
    self.display = "Current"
    self.printmode = "Part"
    self.playing = False

    self.current_detections = {
      "2x2 Green": 0,
      "2x2 Orange": 0,
      "2x2 Yellow": 0,
      "2x3 Yellow": 0,
      "2x4 Green": 0,
      "2x4 Orange": 0,
      "2x4 Yellow": 0,
      "2x4 Gray": 0,
      "2x4 Blue": 0,
      "4x6 Blue": 0,
      "2x8 Gray": 0,
      "2x8 Green": 0,
    }    
    self.video_detections = self.current_detections.copy()

  def dispDetections(self):
    if self.display == "Current":
      detections = self.current_detections
    else:
      detections = self.video_detections

    for part in detections:
      if detections[part] == eel.get_Value(part)():
        pass
      else:
        eel.updateTextSrc(str(detections[part]) + " x ",part)()

  def set_output(self, output_mode):
    self.output = output_mode

  def set_printmode(self, printmode):
    self.printmode = printmode

  def set_display(self, output_mode):
    self.display = output_mode  

  def pause(self):
    self.playing = False
    self.capture.stop_capturing()

  def play(self):
    self.playing = True
    self.capture.restart_capturing()

  def reset_count(self):
    self.video_detections =  { x:0 for x in self.current_detections}

  def switch_video(self, video_name):

    self.current_detections =  { x:0 for x in self.current_detections}
    self.video_detections =  { x:0 for x in self.current_detections}
    self.capture = VideoCamera(video_name)
    self.playing = True

  @eel.expose
  def addValue(self, part):
    text=eel.get_Value(part)()
    val=int(text[0])
    val = val + 1
    eel.updateTextSrc(str(val) + " x ",part)()

  def detect_shape(self, segmented, frame, colour):
    contours, _ = cv2.findContours(segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
      area = cv2.contourArea(cnt)
      approx = cv2.approxPolyDP(cnt, 0.012*cv2.arcLength(cnt, True), True)
      x = approx.ravel()[0]
      y = approx.ravel()[1]   
    return contours

  def segment_green(self, hsv):
    lower = np.array([25, 70, 50], np.uint8) 
    upper = np.array([90, 255, 255], np.uint8) 
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel) 
    return mask

  def segment_orange(self, hsv):
    lower = np.array([0, 130, 50], np.uint8) 
    upper = np.array([15, 255, 255], np.uint8) 
    mask = cv2.inRange(hsv, lower, upper) 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel) 
    return mask

  def segment_yellow(self, hsv):
    lower = np.array([16, 140, 130], np.uint8) 
    upper = np.array([26, 255, 255], np.uint8) 
    mask = cv2.inRange(hsv, lower, upper) 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel) 
    return mask
  
  def segment_blue(self, hsv):
    lower = np.array([80, 60, 40], np.uint8) 
    upper = np.array([140, 255, 255], np.uint8) 
    mask = cv2.inRange(hsv, lower, upper) 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel) 
    return mask

  def segment_gray(self, hsv):
    lower = np.array([0, 0, 0], np.uint8) 
    upper = np.array([180, 50, 150], np.uint8) 
    mask = cv2.inRange(hsv, lower, upper) 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel) 
    return mask

  def detect_bricks_size(self, segmented, color, frame):
    contours, _ = cv2.findContours(segmented, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    part = "No ID"

    if color == "Green":
      outline_code = (60,230,0)
    elif color == "Orange":
      outline_code = (0,154,255)
    elif color == "Yellow":
      outline_code = (0,230,255)
    elif color == "Blue":
      outline_code = (230,205,0)
    else:
      outline_code = (190,190,190)

    for cnt in contours:
      area = cv2.contourArea(cnt)
      approx = cv2.approxPolyDP(cnt, 0.012*cv2.arcLength(cnt, True), True)
      x = approx.ravel()[0]
      y = approx.ravel()[1]

      if area > 2000 and len(approx) < 50:
        #cv2.drawContours(frame, [approx], 0, (255, 255, 255), 1)
        rect = cv2.minAreaRect(cnt)
        _, (width, height), angle = rect
        aspect_ratio = min(width, height) / max(width, height)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        if aspect_ratio > 0.8 and 2500 < area < 6000 and (color == "Green" or color == "Orange" or color == "Yellow"):
          part = "2x2 " + color 
        elif 0.4 < aspect_ratio < 0.62 and 4500 < area < 9500:
          part = "2x4 " + color
        elif 0.55 < aspect_ratio < 0.85 and 2500 < area < 7000 and color == "Yellow":
          part = "2x3 " + color
        elif 0.2 < aspect_ratio < 0.35 and (color == "Green" or color == "Gray"):
          part = "2x8 " + color
        elif 0.55 < aspect_ratio < 0.75 and 10000 < area:
          part = "4x6 " + color
        else:
          part = None

        if part != None:
          cv2.drawContours(frame,[box],0,outline_code,2)   
          self.current_detections[part] = self.current_detections[part] + 1  
          if self.printmode == "Part":
            cv2.putText(frame, part, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
          else:
            cv2.putText(frame, "A = " + str(round(area)) + " AR = " + str(round(aspect_ratio, 2)) + " " + color, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
        else:
          cv2.drawContours(frame,[box],0,(0,0,255),2)   
          cv2.putText(frame, "No ID " + str(area) + " " + str(round(aspect_ratio, 2)) + " " + color, (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))

    return frame

  # Main function for video processing
  def process(self):
    font = cv2.FONT_HERSHEY_COMPLEX
    success, frame = self.capture.get_frame()
    last_detections = None

    while True:

      if self.playing:

        success, frame = self.capture.get_frame()
        img = frame.copy()

        # breaks if in last frame
        if not success:
          break
        blur = cv2.GaussianBlur(frame,(5,5),0)
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        hue, sat, val = cv2.split(hsv)

        #_, gray_th = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)

        self.current_detections =  { x:0 for x in self.current_detections}

        green_th = self.segment_green(hsv)
        frame = self.detect_bricks_size(green_th, "Green", frame)

        orange_th = self.segment_orange(hsv)
        frame = self.detect_bricks_size(orange_th, "Orange", frame)

        yellow_th = self.segment_yellow(hsv)
        frame = self.detect_bricks_size(yellow_th, "Yellow", frame)

        blue_th = self.segment_blue(hsv)
        frame = self.detect_bricks_size(blue_th, "Blue", frame)

        gray_th = self.segment_gray(hsv)
        frame = self.detect_bricks_size(gray_th, "Gray", frame)
        
        if last_detections!=None and self.current_detections==last_detections:
          pass
        else:
          for part in self.current_detections:
            val = self.current_detections[part]
            self.video_detections[part] += val

        last_detections = self.current_detections

        if self.output == "Detection":
          pass
        elif self.output == "Segmentation":
          segmented = cv2.bitwise_or(green_th, orange_th)
          segmented = cv2.bitwise_or(segmented, yellow_th)
          segmented = cv2.bitwise_or(segmented,blue_th)
          segmented = cv2.bitwise_or(segmented, gray_th)
          segmented = cv2.bitwise_and(img, img, mask=segmented)
          frame = segmented
        elif self.output == "Input":
          frame = img

        ids = []
        values = []

        if self.display == "Current":
          for key, elem in self.current_detections.items():
              ids.append(key)
              values.append(str(elem) + " x")
        else:
          for key, elem in self.video_detections.items():
              ids.append(key)
              values.append(str(elem) + " x")

        valuesStr = ",".join(values)
        idStr = ",".join(ids)
        eel.updateListSrc(valuesStr, idStr)()
            
      yield frame
    else:
      pass

