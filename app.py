import threading
import os
import base64
import cv2
import numpy as np
import subprocess
from flask import Flask, render_template, request, jsonify
from firebase_config import db
# from register_face import register_student
from recognize_attendance import start_recognition

app = Flask(__name__, template_folder="templates")

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

DATASET = "dataset"
DATABASE = "database/attendance.db"


@app.route("/")
def home():
    return render_template("index.html")


# @app.route("/register_student", methods=["POST"])
# def register():

#     data = request.json

#     register_student(
#         data["name"],
#         data["roll"],
#         data["dept"],
#         data["images"]
#     )

#     return jsonify({"message": "Student registered"})


@app.route("/register_student", methods=["POST"])
def register_student():

    name = request.json["name"]
    print(name)
    roll = request.json["roll"]
    dept = request.json["dept"]
    images = request.json["images"]

    folder = f"{name}_{roll}"
    path = os.path.join(DATASET, folder)

    os.makedirs(path, exist_ok=True)

    # Save student in firebase...
    db.collection("students").add({
        "name": name,
        "roll_no": roll,
        "department": dept
    })
    
    for i, img in enumerate(images):
        
        img_data = base64.b64decode(img.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5
        )

        for (x, y, w, h) in faces:
            
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            img_path = os.path.join(path, f"img{i}.jpg")

            cv2.imwrite(img_path, face)

            break

# TRAIN MODEL AUTOMATICALLY
    subprocess.run(["python3", "train_model.py"])

    return jsonify({"message": "Student Registered and Model Trained"})


@app.route("/students")
def get_students():

    students = []
    docs = db.collection("students").stream()

    for doc in docs:
        data = doc.to_dict()
        students.append(data)

    return jsonify(students)


@app.route("/start_attendance")
def start_attendance():

    threading.Thread(target=start_recognition).start()

    return jsonify({"message": "Attendance started"})


@app.route("/attendance")
def get_attendance():

    records = []
    docs = db.collection("attendance").stream()

    for doc in docs:
        data = doc.to_dict()
        records.append(data)

    return jsonify(records)


@app.route("/test")
def test():
    return "Server is working"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)