from flask import Flask, render_template, request, jsonify
import numpy as np
from firebase_config import db

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


# REGISTER STUDENT (STORE EMBEDDINGS)
@app.route("/register_student", methods=["POST"])
def register_student():

    data = request.json

    name = data["name"]
    roll = data["roll"]
    dept = data["dept"]
    embeddings = data["embeddings"]

    student_data = {
        "name": name,
        "roll": roll,
        "dept": dept,
        "embeddings": embeddings
    }

    db.collection("students").add(student_data)

    return jsonify({"message": "Student Registered"})


# GET STUDENTS
@app.route("/students")
def students():

    students = db.collection("students").stream()

    data = []

    for s in students:
        d = s.to_dict()
        d["id"] = s.id
        data.append(d)

    return jsonify(data)


# MARK ATTENDANCE
@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():

    embedding = np.array(request.json["embedding"])

    students = db.collection("students").stream()

    best_match = None
    min_dist = 999

    for s in students:
        data = s.to_dict()

        for emb in data["embeddings"]:

            emb = np.array(emb)

            dist = np.linalg.norm(embedding - emb)

            if dist < min_dist:
                min_dist = dist
                best_match = data

    if min_dist < 0.6:  # threshold
        db.collection("attendance").add({
            "name": best_match["name"],
            "roll": best_match["roll"]
        })

        return jsonify({"message": f"Attendance marked for {best_match['name']}"})

    return jsonify({"message": "Face not recognized"})


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))