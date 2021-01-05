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
from processing import VideoProcessing
import threading


# Eeel Functions
@eel.expose
def setup():
  pass

@eel.expose
def video_feed():
  option=eel.get_Value("selected_video")()
  video_name = "./web/image/video/" + str(option) + ".mp4"

  try:
    x.switch_video(video_name)
    text_send_to_js("Selected Video: " + option, "p1")
    y = x.process()
    text_send_to_js("Restart", "btn1")

    for frame in y:
      img_send_to_js(frame, "output")
    text_send_to_js("Video Complete", "p1")
    text_send_to_js("Start Video", "btn1")

  except:
    text_send_to_js("Start", "btn1")
    text_send_to_js("Please select a video", "p1")

@eel.expose
def set_input():
  x.set_output("Input")

@eel.expose
def set_contours():
  x.set_printmode("Properties")
  x.set_output("Detection")

@eel.expose
def set_detection():
  x.set_printmode("Part")
  x.set_output("Detection")
  
@eel.expose
def set_segmentation():
  x.set_output("Segmentation")

@eel.expose
def set_current():
  x.set_display("Current")

@eel.expose
def set_total():
  x.set_display("Total")


@eel.expose
def reset_count():
  x.reset_count()

'''
@eel.expose
def dispDetections():
  if x.display == "Current":
    detections = x.current_detections
  else:
    detections = x.video_detections

  for part in detections:
    eel.updateTextSrc(str(detections[part]) + " x ",part)() 
'''

@eel.expose
def stop_video_feed():
  state=eel.get_Value("btn2")()
  if state=="Pause":
    x.pause()
    text_send_to_js("Video Paused", "p1")
    text_send_to_js("Play", "btn2")
  else:
    x.play()
    text_send_to_js("Video Resumed", "p1")
    text_send_to_js("Pause", "btn2")

def text_send_to_js(val,id):
  eel.updateTextSrc(val,id)()

def img_send_to_js(img, id):
  if np.shape(img) == () :
    
    eel.updateImageSrc("", id)()
  else:
    ret, jpeg = cv2.imencode(".jpg",img)
    jpeg.tobytes()
    blob = base64.b64encode(jpeg) 
    blob = blob.decode("utf-8")
    eel.updateImageSrc(blob, id)()

def start_app():
  try:
    start_html_page = 'index.html'
    eel.init('web')
    logging.info("App Started")
    eel.start('index.html', size=(1000, 800))

  except Exception as e:
    err_msg = 'Could not launch a local server'
    logging.error('{}\n{}'.format(err_msg, e.args))
    show_error(title='Failed to initialise server', msg=err_msg)
    logging.ino('Closing App')
    sys.exit()

if __name__ == "__main__":
  x = VideoProcessing()  
  start_app()