import cv2
import numpy as np
from PIL import Image 
import pickle
import os

from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, db, firestore


cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('entrylog')

# creating pickle file for name list.
'''DO NOT RUN THESE LINES TWICE'''

# names = []
# filename = "names.pkl"
# f = open(filename, 'wb')
# pickle.dump(names,f)
# f.close()

def faceSampling():
#    cam = cv2.VideoCapture('http://192.168.43.1:8080/video')
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height

    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    with open('names.pkl', 'rb') as f:
        names = pickle.load(f)

    name = input('Enter name for the Face: ')
    names.append(name)
    id = names.index(name)

    print('''\n
    Look in the camera Face Sampling has started!.
    Try to move your face and change expression for better face memory registration.\n
    ''')
    # Initialize individual sampling face count
    count = 0

    while(True):

        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1

            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/"+name+"." + str(id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

            cv2.imshow('image', img)

        k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 80: # Take 80 face sample and stop video
             break

    with open('names.pkl', 'wb') as f:
        pickle.dump(names, f)

    # Do a bit of cleanup
    print("Your Face has been registered as {}\n\nExiting Sampling Program".format(name.upper()))
    cam.release()
    cv2.destroyAllWindows()

def faceLearning():
    # Path for face image database
    path = 'dataset'

    recognizer = cv2.face.LBPHFaceRecognizer_create() 
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # function to get the images and label data
    def getImagesAndLabels(path):

        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []

        for imagePath in imagePaths:

            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)

            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)

        return faceSamples,ids

    print ("\nTraining for the faces has been started. It might take a while.\n")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write('trainer/trainer.yml') 

    # Print the numer of faces trained and end program
    print("{0} faces trained. Exiting Training Program".format(len(np.unique(ids))))

def faceRecognition():
    print('\nStarting Recognizer....')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Starting realtime video capture
 #   cam = cv2.VideoCapture('http://192.168.43.1:8080/video')
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    with open('names.pkl', 'rb') as f:
        names = pickle.load(f)

    cond = 1
    while cond:

        ret, img =cam.read()

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match 
            if (confidence > 70):
                id = names[id]
                confidence = "  {0}%".format(round(confidence))
            elif (confidence>100):
                id = "unknown"
                confidence = "  {0}%".format(round(confidence))

            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)
            if (id == "unknown"):
                #if face not detected
                docs = (
                    doc_ref
                    .where("name", "==", "unknown")
                    .stream()
                )
                for doc in docs:
                    doc_ref.document(doc.id).set({"arrivedTime" : datetime.now(), "canAccess" : False}, merge = True)
                
                cond = 0
            else:
                docs = (
                    doc_ref
                    .where("name", "==", "Janice")
                    .stream()
                )
                for doc in docs:
                    doc_ref.document(doc.id).set({"arrivedTime" : datetime.now()}, merge = True)



        cv2.imshow('camera',img) 

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break

    # Do a bit of cleanup
    print("\nExiting Recognizer.")
    cam.release()
    cv2.destroyAllWindows()

def main():
    faceRecognition()

main()