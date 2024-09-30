import cv2
import numpy as np

import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
app = firebase_admin.initialize_app(cred, {'storageBucket': 'anti-theft-detection-2d6d8.appspot.com'})
bucket = storage.bucket()

def get_img():
    blob = bucket.get_blob("unknown.jpg")
    if blob:
        img_data = blob.download_as_bytes()
        arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return img
    else:
        print("Blob not found!")
        exit()

def face_recognition(img):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        face_region = gray[y:y+h, x:x+w]
        label, confidence = recognizer.predict(face_region)
        names = {1: 'Janice', 0: 'Unknown'}
        name = names.get(label, 'Unknown')

        cv2.putText(img, f'{name} ({int(confidence)})', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    cv2.imshow('Face Recognition', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

face_recognition(get_img())