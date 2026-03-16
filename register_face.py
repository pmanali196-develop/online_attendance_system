import os
import base64
import cv2
import numpy as np
from firebase_config import db

DATASET = "dataset"
DATABASE = "database/attendance.db"


def register_student(name, roll_no, department, images):

    student_folder = f"{name}_{roll_no}"
    student_path = os.path.join(DATASET, student_folder)

    os.makedirs(student_path, exist_ok=True)

    db.collection("students").add({
        "name": name,
        "roll_no": roll_no,
        "department": department
    })

    for i, img in enumerate(images):

        img_data = base64.b64decode(img.split(",")[1])
        nparr = np.frombuffer(img_data, np.uint8)

        frame = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        img_path = os.path.join(student_path, f"img{i}.jpg")

        cv2.imwrite(img_path, frame)

    return True