# Src/recommend.py
import numpy as np

def cosine_sim(a, b):
    return np.dot(a, b)

def recommend_items(
    query_emb,
    query_cat,
    all_embs,
    all_ids,
    id2cat,
    topk=5
):
    results = []

    for emb, iid in zip(all_embs, all_ids):
        if id2cat[iid] == query_cat:
            continue
        sim = cosine_sim(query_emb, emb)
        results.append((iid, sim))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:topk]
