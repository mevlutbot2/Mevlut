import face_recognition
import picamera
import numpy as np
import os

camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

known_encodings = []
known_names = []

path = "/home/pi/Desktop/images"
files = [next(f for f in os.walk(path))[2]]

print("Loading...")
print(files)
for file in files[0]:
    image = face_recognition.load_image_file(path + "/" + str(file))
    encoding = face_recognition.face_encodings(image)[0]
    known_encodings.append(encoding)
    known_names.append(file.split(".")[0])

face_locations = []
face_encodings = []

print("Loaded images")

while True:
    print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format="rgb")

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(output)
    print("Found {} faces in image.".format(len(face_locations)))
    face_encodings = face_recognition.face_encodings(output, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        match = face_recognition.compare_faces(known_encodings, face_encoding)
        name = "<Unknown Person>"

        if True in match:
            name = known_names[match.index(True)]

        print("I see someone named {}!".format(name))