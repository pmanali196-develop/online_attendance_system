from insightface.app import FaceAnalysis
import numpy as np

app = None

def load_model():
    global app
    if app is None:
        app = FaceAnalysis(name='buffalo_s')    # smaller model
        app.prepare(ctx_id=-1)  # force CPU


def get_embedding(image):

    load_model()
    
    faces = app.get(image)

    if len(faces) == 0:
        return None

    return faces[0].embedding


def compare_embeddings(emb1, emb2):

    emb1 = np.array(emb1)
    emb2 = np.array(emb2)

    dist = np.linalg.norm(emb1 - emb2)

    return dist < 1.0, dist   # strict threshold