import numpy as np

emb = np.load("ml_models/item_embeddings.npy")

# similarity giữa 2 item bất kỳ
sim = emb[0] @ emb[1000]
print(sim)

# độ lệch giữa các vector
print(np.std(emb, axis=0).mean())
