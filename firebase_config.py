import firebase_admin
from firebase_admin import credentials, firestore, storage
# import os
# import json

# cred = credentials.Certificate("firebase_key.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()

# firebase_key = json.loads(os.environ["FIREBASE_KEY"])

# cred = credentials.Certificate(firebase_key)

cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'face-attendance-system-7fccd.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()