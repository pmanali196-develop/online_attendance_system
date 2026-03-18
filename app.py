# import threading
import os
import base64
import numpy as np
import cv2
# import subprocess
# import sys
import uuid
from flask import Flask, render_template, request, jsonify
from firebase_config import db
from face_engine import get_embedding, compare_embeddings
# from recognize_attendance import start_recognition
# from register_face import register_student


app = Flask(__name__, static_folder="static", template_folder="templates")

# face_cascade = cv2.CascadeClassifier(
#     cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
# )


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/register_student", methods=["POST"])
# def register_student():

#     try:

#         data = request.get_json()
#         name = data.get("name")
#         print(name)
#         roll = data.get("roll")
#         dept = data.get("dept")
#         images = data.get("images", [])

#         print("Images received:", len(images))
        
#         folder = f"{name}_{roll}"
#         path = os.path.join(DATASET, folder)

#         os.makedirs(path, exist_ok=True)

#         # Save student in firebase...
#         db.collection("students").add({
#             "name": name,
#             "roll_no": roll,
#             "department": dept
#         })
        
#         for i, img in enumerate(images):
            
#             img_data = base64.b64decode(img.split(",")[1])
#             nparr = np.frombuffer(img_data, np.uint8)

#             frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#             faces = face_cascade.detectMultiScale(
#                 gray,
#                 scaleFactor=1.3,
#                 minNeighbors=5
#             )

#             for (x, y, w, h) in faces:
                
#                 face = gray[y:y+h, x:x+w]
#                 face = cv2.resize(face, (200, 200))

#                 img_path = os.path.join(path, f"img{i}.jpg")

#                 cv2.imwrite(img_path, face)

#                 break

#     # TRAIN MODEL AUTOMATICALLY
#         subprocess.run([sys.executable, "train_model.py"])

#         return jsonify({"message": "Student Registered and Model Trained"})

#     except Exception as e:
#         print("Error:", e)
#         return jsonify({"error": str(e)}), 500


# 🔥 Upload image to Firebase Storage
def upload_image_to_firebase(image_bytes):
    filename = f"faces/{uuid.uuid4()}.jpg"
    blob = bucket.blob(filename)

    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    blob.make_public()  # optional

    return blob.public_url


@app.route("/register_student", methods=["POST"])
def register():

    data = request.json

    name = data["name"]
    roll = data["roll"]
    dept = data["dept"]
    images = data["images"]

    embeddings = []
    image_urls = []

    for img in images:

        img_data = base64.b64decode(img.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        emb = get_embedding(frame)

        if emb is None:
            continue

        embeddings.append(emb.tolist())

        url = upload_image_to_firebase(img_data)
        image_urls.append(url)

    if len(embeddings) == 0:
        return jsonify({"message": "No face detected"}), 400

    # store average embedding
    avg_embedding = np.mean(embeddings, axis=0).tolist()

    db.collection("students").document(roll).set({
        "name": name,
        "roll": roll,
        "dept": dept,
        "embedding": avg_embedding,
        "images": image_urls
    })

    return jsonify({"message": "Student registered successfully"})


# @app.route("/students")
# def get_students():

#     students = []
#     docs = db.collection("students").stream()

#     for doc in docs:
#         data = doc.to_dict()
#         students.append(data)

#     return jsonify(students)


# @app.route("/start_attendance")
# def start_attendance():

#     threading.Thread(target=start_recognition).start()

#     return jsonify({"message": "Attendance started"})


@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():

    img = request.json["image"]

    img_data = base64.b64decode(img.split(",")[1])
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    emb = get_embedding(frame)

    if emb is None:
        return jsonify({"message": "No face detected"})

    students = db.collection("students").stream()

    for student in students:

        data = student.to_dict()

        match, dist = compare_embeddings(emb, data["embedding"])

        if match:
            db.collection("attendance").add({
                "name": data["name"],
                "roll": data["roll"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            return jsonify({"message": f"Attendance marked for {data['name']}"})

    return jsonify({"message": "Face not recognized"})


# @app.route("/attendance")
# def get_attendance():

#     records = []
#     docs = db.collection("attendance").stream()

#     for doc in docs:
#         data = doc.to_dict()
#         records.append(data)

#     return jsonify(records)


@app.route("/test")
def test():
    return "Server is working"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)