import numpy as np

def cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0

    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
