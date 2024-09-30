import cv2
import numpy as np

import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
app = firebase_admin.initialize_app(cred, {'storageBucket': 'anti-theft-detection-2d6d8.appspot.com'})
bucket = storage.bucket()

def send_img():
    file = "person.jpg"
    blob = bucket.blob(file)
    blob.upload_from_filename(file)
    print("file sent")
    

def get_img():
    # bucket = storage.bucket()
    blob = bucket.get_blob("person.jpg") #blob
    if blob:
        img_data = blob.download_as_bytes()
        arr = np.frombuffer(img_data, np.uint8)  # array of bytes
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # actual image
        
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Blob not found!")

get_img()
