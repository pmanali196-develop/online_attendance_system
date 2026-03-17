import cv2
import numpy as np
from firebase_config import db, bucket
from face_engine import get_embedding
import uuid

# 🔥 Upload image to Firebase Storage
def upload_image(image):

    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = buffer.tobytes()

    filename = f"faces/{uuid.uuid4()}.jpg"
    blob = bucket.blob(filename)

    blob.upload_from_string(image_bytes, content_type='image/jpeg')
    blob.make_public()

    return blob.public_url


def register_student():

    name = input("Enter Name: ")
    roll = input("Enter Roll No: ")
    dept = input("Enter Department: ")

    cap = cv2.VideoCapture(0)

    embeddings = []
    image_urls = []

    print("📸 Capturing faces... Press 'q' to stop")

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Register Face", frame)

        emb = get_embedding(frame)

        if emb is not None:

            embeddings.append(emb.tolist())

            url = upload_image(frame)
            image_urls.append(url)

            print(f"Captured: {len(embeddings)}")

        # Stop after 5 images
        if len(embeddings) >= 5:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(embeddings) == 0:
        print("❌ No face detected")
        return

    avg_embedding = np.mean(embeddings, axis=0).tolist()

    db.collection("students").document(roll).set({
        "name": name,
        "roll": roll,
        "dept": dept,
        "embedding": avg_embedding,
        "images": image_urls
    })

    print("✅ Student registered successfully!")


if __name__ == "__main__":
    register_student()