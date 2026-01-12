import torch
import numpy as np
import os
from PIL import Image
from torchvision import transforms

from item_encoder import ItemEncoder  

MODEL_PATH = "ml_models/item_encoder_best.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = ItemEncoder().to(DEVICE)
state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
model.load_state_dict(state_dict)
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

EMB_DIR = "ml_models/embeddings"
os.makedirs(EMB_DIR, exist_ok=True)

def embed_image(image_path: str):
    image = Image.open(image_path).convert("RGB")
    x = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        emb = model(x).cpu().numpy()[0]

    fname = os.path.basename(image_path).split(".")[0] + ".npy"
    save_path = os.path.join(EMB_DIR, fname)
    np.save(save_path, emb)


    return {
        "embedding_path": save_path
    }
