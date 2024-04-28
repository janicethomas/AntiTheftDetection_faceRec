'''
collection name - entrylog
every document in entrylog has an auto generated id
attributes - name(string), canAccess(boolean), arrivedTime(time)
'''
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, db, firestore


cred = credentials.Certificate('./anti-theft-detection-2d6d8-firebase-adminsdk.json')
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('entrylog')


# add new person
data = {
    'name' : 'Janice',
    'canAccess' : True,
    'arrivedTime' : datetime.now()
}
doc_ref.add(data)


# to update the canAccess variable depending on whether a person is detected
#if detected
docs = (
    doc_ref
    .where("name", "==", "Nikita")
    .stream()
)
for doc in docs:
    doc_ref.document(doc.id).set({"arrivedTime" : datetime.now()}, merge = True)

#if face not detected
docs = (
    doc_ref
    .where("name", "==", "unknown")
    .stream()
)
for doc in docs:
    doc_ref.document(doc.id).set({"arrivedTime" : datetime.now(), "canAccess" : False}, merge = True)


#for servo motor
cond = True
while cond:
    docs = (
        doc_ref
        .where("arrivedTime", ">", datetime.now() - timedelta(0,5))
        .stream()
    )

    # print(docs)

    for doc in docs:
        print("door opens, delay, door closes")
        cond = False
        break


# to see the database values
docs = doc_ref.stream()

for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")
