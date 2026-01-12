import torch
import torch.nn as nn
from torchvision import models
from utils.image_utils import load_image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

LABELS = [
    "accessories",
    "bag",
    "bottoms",
    "dress",
    "others",
    "shoes",
    "tops"
]

num_classes = len(LABELS)

# ===== INIT MODEL (Y HỆT TRAIN) =====
model = models.mobilenet_v2(
    weights=models.MobileNet_V2_Weights.DEFAULT
)
model.classifier[1] = nn.Linear(
    model.last_channel,
    num_classes
)

state_dict = torch.load(
    "ml_models/category_classifier.pth",
    map_location=DEVICE
)
model.load_state_dict(state_dict)

model.to(DEVICE)
model.eval()

# ===== CLASSIFY =====
@torch.no_grad()
def classify_image(image_path: str):
    x = load_image(image_path).to(DEVICE)
    out = model(x)

    prob = torch.softmax(out, dim=1)
    conf, idx = torch.max(prob, dim=1)

    label = LABELS[idx.item()]

    return {
        "label": label,          # 🔥 LABEL GỐC
        "confidence": float(conf.item())
    }
