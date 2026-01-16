# Src/test_recommend.py
import os
import random
import torch
import numpy as np
from PIL import Image
from torchvision import transforms

from item_encoder import ItemEncoder
from recommend import recommend_items

# ================= CONFIG =================
DATA_DIR = "data/cleaned_maryland_processed/train"
MODEL_PATH = "ml_models/item_encoder_best.pth"
EMB_PATH = "ml_models/item_embeddings.npy"
ID_PATH = "ml_models/item_ids.txt"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ================= LOAD EMBEDDINGS =================
print(" Loading embedding database...")
all_embs = np.load(EMB_PATH)
with open(ID_PATH) as f:
    all_ids = [line.strip() for line in f]

print("Total items:", len(all_ids))

# ================= BUILD id → category =================
id2cat = {}
id2path = {}

for cat in os.listdir(DATA_DIR):
    cat_dir = os.path.join(DATA_DIR, cat)
    for f in os.listdir(cat_dir):
        if f.endswith(".jpg"):
            iid = f.split(".")[0]
            id2cat[iid] = cat
            id2path[iid] = os.path.join(cat_dir, f)

# ================= LOAD MODEL =================
model = ItemEncoder().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

# ================= RANDOM QUERY =================
query_id = random.choice(list(id2cat.keys()))
query_cat = id2cat[query_id]
query_path = id2path[query_id]

print("\n Query item:", query_id)
print("Category:", query_cat)

img = tf(Image.open(query_path).convert("RGB")).unsqueeze(0).to(DEVICE)

with torch.no_grad():
    query_emb = model(img).cpu().numpy()[0]

# ================= RECOMMEND =================
recs = recommend_items(
    query_emb,
    query_cat,
    all_embs,
    all_ids,
    id2cat,
    topk=6
)

print("\n Recommended items:")
for iid, score in recs:
    print(f"{iid:>15} | {id2cat[iid]:>12} | sim={score:.3f}")
