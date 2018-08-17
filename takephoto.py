import picamera

name = input("Enter name: ")
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.capture("/home/pi/Desktop/images/" + name + ".jpg")
