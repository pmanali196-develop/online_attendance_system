import os
import cv2
import numpy as np
import pickle

dataset_path = "dataset"
trainer_path = "trainer"

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []
label_map = {}

current_label = 0

for folder in os.listdir(dataset_path):

    folder_path = os.path.join(dataset_path, folder)

    if not os.path.isdir(folder_path):
        continue

    label_map[current_label] = folder

    for file in os.listdir(folder_path):

        img_path = os.path.join(folder_path, file)

        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        faces.append(img)
        labels.append(current_label)

    current_label += 1

labels = np.array(labels)

recognizer.train(faces, labels)

os.makedirs(trainer_path, exist_ok=True)

recognizer.save("trainer/face_model.yml")

with open("trainer/labels.pkl", "wb") as f:
    pickle.dump(label_map, f)

print("✅ Model trained successfully")