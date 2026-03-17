import cv2
import numpy as np
from datetime import datetime

from firebase_config import db
from face_engine import get_embedding, compare_embeddings


def recognize():

    cap = cv2.VideoCapture(0)

    print("🎥 Starting Attendance... Press 'q' to quit")

    # Load all students from Firestore
    students = []
    docs = db.collection("students").stream()

    for doc in docs:
        data = doc.to_dict()
        students.append(data)

    marked = set()  # to avoid duplicate attendance

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        emb = get_embedding(frame)

        if emb is not None:

            for student in students:

                match, dist = compare_embeddings(emb, student["embedding"])

                if match and student["roll"] not in marked:

                    print(f"✅ Recognized: {student['name']} (Dist: {dist:.2f})")

                    db.collection("attendance").add({
                        "name": student["name"],
                        "roll": student["roll"],
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    marked.add(student["roll"])

        cv2.imshow("Attendance System", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    recognize()