from flask import Flask, render_template, request
#!usr/bin/python
import numpy as np
import cv2
from time import sleep
import RPi.GPIO as GPIO
import google.assistant.library as google

#GPIO pins
Forward = 18
Backward = 23

Forward2 = 22
Backward2 = 27

#Motors
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Forward, GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)
GPIO.setup(Forward2, GPIO.OUT)
GPIO.setup(Backward2, GPIO.OUT)

#PWM
GPIO.setup(16,GPIO.OUT)
GPIO.setup(20,GPIO.OUT)
pwm = GPIO.PWM(16, 100)
pwm.start(40)
pwm2 = GPIO.PWM(20, 100)
pwm2.start(40)

#Stopping motors on start
GPIO.output(Forward, GPIO.LOW)
GPIO.output(Forward2, GPIO.LOW)
GPIO.output(Backward, GPIO.LOW)
GPIO.output(Backward2, GPIO.LOW)

app = Flask(__name__)

@app.route('/setMotor', methods=['GET', 'POST'])
#Usage: /setMotor?motor=forward
def setMotor():
    pin = Forward
    pin2 = Forward2
    motor = request.values['motor']
    
    if motor.lower().__contains__("backward"):
        pin = Backward
        pin2 = Backward2

    elif motor.lower().__contains__("right"):
        pin = Forward2
        pin2 = Backward

    elif motor.lower().__contains__("left"):
        pin = Forward
        pin2 = Backward2
        
    GPIO.output(pin, GPIO.HIGH)
    GPIO.output(pin2, GPIO.HIGH)
    sleep(5)
    GPIO.output(pin, GPIO.LOW)
    GPIO.output(pin2, GPIO.LOW)
                           
    return "Motor: %s" % (motor)


@app.route('/followLine', methods=['GET', 'POST'])
#Usage: /followLine
def followline():
    video = cv2.VideoCapture(-1)
    video.set(3, 160)
    video.set(4, 120)

    GPIO.output(Forward, GPIO.HIGH)
    GPIO.output(Forward2, GPIO.HIGH)
    
    while(True):
 
        # Capture the frames
        ret, frame = video.read()
     
        # Crop the image
        crop_img = frame[60:120, 0:160]
     
        # Convert to grayscale
        gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
     
        # Gaussian blur
        blur = cv2.GaussianBlur(gray,(5,5),0)
     
        # Color thresholding
        ret,thresh1 = cv2.threshold(blur,60,255,cv2.THRESH_BINARY_INV)
     
        # Erode and dilate to remove accidental line detections
        mask = cv2.erode(thresh1, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
     
        # Find the contours of the frame
        contours,hierarchy = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
     
        # Find the biggest contour (if detected)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
     
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
     
            cv2.line(crop_img,(cx,0),(cx,720),(255,0,0),1)
            cv2.line(crop_img,(0,cy),(1280,cy),(255,0,0),1)
     
            cv2.drawContours(crop_img, contours, -1, (0,255,0), 1)
     
            print "cx:" + str(cx)
            print ""
     
            if cx >= 120:
                turnRight()
     
            if cx < 120 and cx > 50:
                GPIO.output(Forward, GPIO.HIGH)
                GPIO.output(Forward2, GPIO.HIGH)
     
            if cx <= 50:
                turnLeft()
     
        else:
            turnRight()
     
     
        #Display the resulting frame
        cv2.imshow('frame',crop_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    
if __name__ == "__main__":
    app.run('10.0.89.215', 9999)

def turnLeft():
    GPIO.output(Forward, GPIO.HIGH)
    GPIO.output(Forward2, GPIO.LOW)
    GPIO.output(Backward, GPIO.LOW)
    GPIO.output(Backward2, GPIO.HIGH)

def turnRight():
    GPIO.output(Forward, GPIO.LOW)
    GPIO.output(Forward2, GPIO.HIGH)
    GPIO.output(Backward, GPIO.HIGH)
    GPIO.output(Backward2, GPIO.LOW)
                
