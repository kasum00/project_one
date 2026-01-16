# ==================================================
# test_recommend_show.py
# Similar Item Recommendation (CORRECT VERSION)
# ==================================================

import os
import random
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

# =========================
# CONFIG
# =========================
EMB_PATH = "ml_models/item_embeddings.npy"
ID_PATH  = "ml_models/item_ids.txt"
IMAGE_ROOT = "data/Re-PolyVore"
TOP_K = 5

# =========================
# LOAD EMBEDDINGS
# =========================
print(" Loading embeddings...")
emb = np.load(EMB_PATH).astype("float32")

with open(ID_PATH, "r") as f:
    item_ids = [line.strip() for line in f]

N, D = emb.shape
print(f" Loaded {N} items | dim = {D}")

# =========================
# BUILD IMAGE + CATEGORY MAP
# =========================
print(" Building image & category map...")

id_to_path = {}
id_to_cat = {}

for cat in os.listdir(IMAGE_ROOT):
    cat_dir = os.path.join(IMAGE_ROOT, cat)
    if not os.path.isdir(cat_dir):
        continue

    for f in os.listdir(cat_dir):
        if f.lower().endswith(".jpg"):
            item_id = os.path.splitext(f)[0]
            id_to_path[item_id] = os.path.join(cat_dir, f)
            id_to_cat[item_id] = cat

print(f" Indexed {len(id_to_path)} images")

# =========================
# PICK RANDOM QUERY ITEM
# =========================
valid_indices = [
    i for i in range(N)
    if item_ids[i] in id_to_cat
]

QUERY_INDEX = random.choice(valid_indices)

query_id = item_ids[QUERY_INDEX]
query_emb = emb[QUERY_INDEX]
query_cat = id_to_cat[query_id]

print(f"\n Query item: {query_id} ({query_cat})")

# =========================
# COSINE SIMILARITY
# =========================
sims = emb @ query_emb
sims[QUERY_INDEX] = -1.0

# =========================
# TOP-K SIMILAR ITEMS (SAME CATEGORY)
# =========================
candidates = np.argsort(-sims)

top_items = []
for idx in candidates:
    if id_to_cat.get(item_ids[idx]) == query_cat:
        top_items.append((idx, sims[idx]))
    if len(top_items) == TOP_K:
        break

# =========================
# DEBUG PRINT
# =========================
print("\n Similar items:")
for idx, score in top_items:
    print(
        f"{query_cat:12s} "
        f"{score:.3f}  "
        f"{item_ids[idx]}"
    )

# =========================
# VISUALIZE
# =========================
fig, axes = plt.subplots(1, TOP_K + 1, figsize=(16, 4))

# Query
axes[0].imshow(Image.open(id_to_path[query_id]))
axes[0].set_title(f"QUERY\n{query_cat}")
axes[0].axis("off")

# Similar items
for ax, (idx, score) in zip(axes[1:], top_items):
    item_id = item_ids[idx]
    ax.imshow(Image.open(id_to_path[item_id]))
    ax.set_title(f"{query_cat}\n{score:.2f}")
    ax.axis("off")

plt.tight_layout()
plt.savefig("recommend_result.png", dpi=150)
plt.close()

print("\n Saved: recommend_result.png")
