import os
import random
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ===== PATHS (THEO SETUP CỦA BẠN) =====
EMB_PATH = "ml_service/ml_models/item_embeddings.npy"
ID_PATH = "ml_service/ml_models/item_ids.txt"
SUBLABEL_ROOT = "data/Re-PolyVore"

# ===== LOAD =====
emb = np.load(EMB_PATH).astype("float32")
with open(ID_PATH) as f:
    item_ids = [line.strip() for line in f]

# ===== BUILD SUBLABEL MAP FROM Re-PolyVore =====
id_to_sublabel = {}

for sub in os.listdir(SUBLABEL_ROOT):
    sub_dir = os.path.join(SUBLABEL_ROOT, sub)
    if not os.path.isdir(sub_dir):
        continue

    for f in os.listdir(sub_dir):
        if f.lower().endswith(".jpg"):
            iid = os.path.splitext(f)[0]
            id_to_sublabel[iid] = sub

print("Total sublabels found:", len(set(id_to_sublabel.values())))

# =====================================================
# 🔍 TEST 1: NEAREST NEIGHBOR (SKIRT)
# =====================================================
print("\n=== NEAREST NEIGHBOR TEST (SKIRT) ===")

skirt_indices = [
    i for i, iid in enumerate(item_ids)
    if id_to_sublabel.get(iid) == "skirt"
]

if not skirt_indices:
    raise ValueError("No skirt items found")
QUERY_ID = "2825739_10" 

query_idx = None
for i, iid in enumerate(item_ids):
    if iid == QUERY_ID:
        query_idx = i
        break

if query_idx is None:
    raise ValueError(f"Query ID {QUERY_ID} not found in item_ids.txt")

query_emb = emb[query_idx]

sims = cosine_similarity([query_emb], emb)[0]
top_idx = sims.argsort()[::-1][1:21]

print("Query:", item_ids[query_idx])

for i in top_idx:
    print(f"{id_to_sublabel.get(item_ids[i], 'UNK'):12s}  {sims[i]:.3f}")

# =====================================================
# 🧪 TEST 2: LINEAR PROBE (QUAN TRỌNG NHẤT)
# =====================================================
print("\n=== LINEAR PROBE TEST ===")

X, y = [], []

for i, iid in enumerate(item_ids):
    if iid in id_to_sublabel:
        X.append(emb[i])
        y.append(id_to_sublabel[iid])

X = np.array(X)
y = np.array(y)

le = LabelEncoder()
y_enc = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

clf = LogisticRegression(max_iter=2000, n_jobs=-1)
clf.fit(X_train, y_train)

acc = clf.score(X_test, y_test)
print("Linear probe accuracy:", round(acc, 4))
