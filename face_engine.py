from insightface.app import FaceAnalysis
import numpy as np

app = FaceAnalysis()
app.prepare(ctx_id=0)

def get_embedding(image):

    faces = app.get(image)

    if len(faces) == 0:
        return None

    return faces[0].embedding


def compare_embeddings(emb1, emb2):

    emb1 = np.array(emb1)
    emb2 = np.array(emb2)

    dist = np.linalg.norm(emb1 - emb2)

    return dist < 1.0, dist   # strict threshold