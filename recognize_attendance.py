import cv2
import pickle
from firebase_config import db
from datetime import datetime

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/face_model.yml")

with open("trainer/labels.pkl", "rb") as f:
    label_map = pickle.load(f)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

DATABASE = "database/attendance.db"


def mark_attendance(student_name, roll_no):

    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    # Check if already marked today
    docs = db.collection("attendance") \
        .where("roll_no", "==", roll_no) \
        .where("date", "==", today) \
        .stream()

    if len(list(docs)) == 0:

        db.collection("attendance").add({
            "name": student_name,
            "roll_no": roll_no,
            "date": today,
            "time": time_now,
            "status": "Present"
        })

def start_recognition():

    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray,1.2,5)

        for (x,y,w,h) in faces:

            face_roi = gray[y:y+h, x:x+w]

            label, confidence = recognizer.predict(face_roi)

            if confidence < 70:

                student_folder = label_map[label]
                name, roll = student_folder.rsplit("_",1)

                mark_attendance(name, roll)

        cv2.imshow("Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()