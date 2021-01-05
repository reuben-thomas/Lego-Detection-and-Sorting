import cv2
import numpy as np
import os, os.path
import random as rng

class VideoCamera(object):

  def __init__(self, id):

    self.VIDEO_DEVICE = 0
        
    if id:
      self.video = cv2.VideoCapture(id)
    else:
      self.video = cv2.VideoCapture(self.VIDEO_DEVICE, cv2.CAP_DSHOW)

    self.IMAGE_WIDTH = int(self.video.get(3))
    self.IMAGE_HEIGHT = int(self.video.get(4))

    self.active = True
    self.last_frame = np.zeros((self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 3), np.uint8)
    
    success, self.last_frame = self.video.read()    
    
  def __del__(self):
    self.video.release()

  def stop_capturing(self):
    self.active = False

  def restart_capturing(self):
    self.active = True

  def get_frame(self):
    success = False
    if self.active == True:
      success, frame = self.video.read()
      if success:
          self.last_frame = frame
    return success,self.last_frame 
         
   

      
     

# OPENCV FUNCITONS
def increase_brightness(img, value):
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
  h, s, v = cv2.split(hsv)

  lim = 255 - value
  v[v > lim] = 255
  v[v <= lim] += value

  final_hsv = cv2.merge((h, s, v))
  img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
  return img
