# Src/build_embedding_db.py

import os
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from tqdm import tqdm

from item_encoder import ItemEncoder

# ================= CONFIG =================
IMAGE_ROOT = "data/Re-PolyVore"
MODEL_PATH = "ml_models/item_encoder_best.pth"
OUT_EMB = "ml_models/item_embeddings.npy"
OUT_IDS = "ml_models/item_ids.txt"

BATCH_SIZE = 64
VALID_EXT = (".jpg", ".jpeg", ".png")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ================= TRANSFORM =================
tf = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# ================= LOAD MODEL =================
model = ItemEncoder().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# ================= COLLECT IMAGE PATHS =================
image_paths = []
image_ids = []

for cat in os.listdir(IMAGE_ROOT):
    cat_dir = os.path.join(IMAGE_ROOT, cat)
    if not os.path.isdir(cat_dir):
        continue

    for f in os.listdir(cat_dir):
        if f.lower().endswith(VALID_EXT):
            image_paths.append(os.path.join(cat_dir, f))
            image_ids.append(os.path.splitext(f)[0])

print(f" Total images: {len(image_paths)}")

# ================= BUILD EMBEDDINGS (BATCH) =================
embs = []

with torch.no_grad():
    for i in tqdm(range(0, len(image_paths), BATCH_SIZE), desc="🔨 Encoding"):
        batch_paths = image_paths[i:i+BATCH_SIZE]

        imgs = [
            tf(Image.open(p).convert("RGB"))
            for p in batch_paths
        ]
        imgs = torch.stack(imgs).to(device)

        emb = model(imgs)
        emb = torch.nn.functional.normalize(emb, dim=1)

        embs.append(emb.cpu().numpy())

# ================= SAVE =================
embs = np.vstack(embs)
np.save(OUT_EMB, embs)

with open(OUT_IDS, "w") as f:
    for i in image_ids:
        f.write(i + "\n")

print(f"\n Saved embeddings: {embs.shape}")
