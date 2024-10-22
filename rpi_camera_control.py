'''
collection name - cameralog
'''

import firebase_admin
from firebase_admin import credentials, db, firestore


cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('cameralog')


# to update the camera-on variable depending on whether a person is detected
#if detected
docs = (
    doc_ref
    .where("cameraOn", "==", "false")
    .stream()
)

def setTrue():
    docs = (
        doc_ref
        .where("cameraOn", "==", "false")
        .stream()
    )
    for doc in docs:
        doc_ref.document(doc.id).set({"cameraOn":"true"}, merge = True)

def setFalse():
    docs = (
        doc_ref
        .where("cameraOn", "==", "true")
        .stream()
    )
    for doc in docs:
        doc_ref.document(doc.id).set({"cameraOn":"false"}, merge = True)


setTrue()