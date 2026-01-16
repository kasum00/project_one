# ==================================================
# test_outfit.py
# Outfit recommendation - FINAL (diverse + fashion rules)
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

TOP_K_PER_GROUP = 10   # random trong top-K

# =========================
# CATEGORY DEFINITIONS
# =========================
TOPS = {"top"}
OUTWEAR = {"outwear"}

BOTTOMS_MAIN = {"pants", "skirt"}
LEGWEAR = {"legwear"}         

ONEPIECE = {"dress", "jumpsuit"}

SHOES = {"shoes"}
BAG = {"bag"}

ACCESSORIES = {
    "bracelet", "rings", "necklace", "earrings", "brooch", "watches",
    "hairwear", "hats", "eyewear", "gloves", "neckwear"
}

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
print(" Indexing images...")

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
# PICK RANDOM QUERY (VALID)
# =========================
VALID_QUERY_CATS = (
    TOPS | OUTWEAR | BOTTOMS_MAIN |
    ONEPIECE | SHOES | BAG | ACCESSORIES
)

valid_indices = [
    i for i in range(N)
    if id_to_cat.get(item_ids[i]) in VALID_QUERY_CATS
]

QUERY_INDEX = random.choice(valid_indices)

query_id = item_ids[QUERY_INDEX]
query_emb = emb[QUERY_INDEX]
query_cat = id_to_cat[query_id]

print(f"\n Query item: {query_id} ({query_cat})")

# =========================
# OUTFIT LOGIC (FASHION RULES)
# =========================
if query_cat in ONEPIECE:
    target_groups = [SHOES, BAG, ACCESSORIES, LEGWEAR]

elif query_cat in TOPS:
    target_groups = [BOTTOMS_MAIN, SHOES, BAG, OUTWEAR]

elif query_cat in OUTWEAR:
    target_groups = [TOPS, BOTTOMS_MAIN, SHOES, BAG]

elif query_cat == "skirt":
    target_groups = [TOPS, SHOES, BAG, LEGWEAR]

elif query_cat == "pants":
    target_groups = [TOPS, SHOES, BAG]

elif query_cat in SHOES:
    target_groups = [BOTTOMS_MAIN, TOPS, BAG, OUTWEAR]

elif query_cat in BAG or query_cat in ACCESSORIES:
    target_groups = [TOPS, BOTTOMS_MAIN, SHOES, OUTWEAR]

elif query_cat in LEGWEAR:
    print("Legwear cannot be a standalone query.")
    exit(0)

else:
    target_groups = [TOPS, BOTTOMS_MAIN, SHOES]

# =========================
# COSINE SIMILARITY
# =========================
sims = emb @ query_emb

# =========================
# PICK ITEM PER GROUP (RANDOM IN TOP-K)
# =========================
outfit = []

for group in target_groups:
    candidates = []

    for i in range(N):
        if id_to_cat.get(item_ids[i]) in group:
            candidates.append((i, sims[i]))

    if not candidates:
        continue

    candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = candidates[:TOP_K_PER_GROUP]

    # ===== LEGWEAR CONSTRAINT =====
    if group == LEGWEAR:
        has_skirt = any(id_to_cat[item_ids[i]] == "skirt" for i, _ in outfit)
        has_dress = any(id_to_cat[item_ids[i]] in ONEPIECE for i, _ in outfit)
        if not (has_skirt or has_dress):
            continue

    # ===== RANDOM WITH WEIGHT (OPTIONAL BUT NICE) =====
    scores = np.array([s for _, s in top_candidates])
    scores = scores - scores.min() + 1e-6
    probs = scores / scores.sum()

    chosen = random.choices(
        top_candidates,
        weights=probs,
        k=1
    )[0]

    outfit.append(chosen)

# =========================
# CHECK RESULT
# =========================
if not outfit:
    print("Outfit empty. Check rules.")
    exit(0)

# =========================
# DEBUG PRINT
# =========================
print("\nOutfit suggestion:")
print(f"QUERY ({query_cat}): {query_id}")

for idx, score in outfit:
    print(
        f"{id_to_cat[item_ids[idx]]:12s} "
        f"{score:.3f} "
        f"{item_ids[idx]}"
    )

# =========================
# VISUALIZE
# =========================
fig, axes = plt.subplots(1, len(outfit) + 1, figsize=(18, 4))

axes[0].imshow(Image.open(id_to_path[query_id]))
axes[0].set_title(f"QUERY\n{query_cat}")
axes[0].axis("off")

for ax, (idx, score) in zip(axes[1:], outfit):
    item_id = item_ids[idx]
    ax.imshow(Image.open(id_to_path[item_id]))
    ax.set_title(f"{id_to_cat[item_id]}\n{score:.2f}")
    ax.axis("off")

plt.tight_layout()
plt.savefig("outfit_result.png", dpi=150)
plt.close()

print("\n Saved: outfit_result.png")
