import cv2
import numpy as np
from PIL import Image 
import pickle
import os
import time

from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, db, firestore


cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('entrylog')
doc_ref2 = db.collection('cameralog')


def checkFirebase():
                docs = (
                    doc_ref
                    .where("name", "==", "unknown")
                    .stream()
                )
                for doc in docs:
                    print(doc.to_dict()['canAccess'])
                


def main():
    checkFirebase()
                


main()