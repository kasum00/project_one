import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

EMB_PATH = "ml_models/item_embeddings.npy"
IDS_PATH = "ml_models/item_ids.txt"

embeddings = np.load(EMB_PATH)

with open(IDS_PATH, encoding="utf-8") as f:
    item_ids = [line.strip() for line in f if line.strip()]


assert len(item_ids) == embeddings.shape[0], \
    "item_ids và embeddings KHÔNG cùng kích thước"

def recommend(embedding, top_k=5):
    sims = cosine_similarity(
        embedding.reshape(1, -1),
        embeddings
    )[0]

    top_idx = sims.argsort()[::-1][1:top_k+1]

    return [
        {
            "item_key": item_ids[i],     # ← string ID
            "similarity": float(sims[i])
        }
        for i in top_idx
    ]
