import os
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from item_encoder import ItemEncoder
from pair_dataset import PairDataset
from utils import load_compatibility

DATA_ROOT = "data/cleaned_maryland_processed/train"
COMPAT_FILE = "data/cleaned_maryland_processed/compatibility_train.txt"
MODEL_SAVE = "ml_models/item_encoder_best.pth"

BATCH_SIZE = 64
EPOCHS = 20
LR = 1e-4

def info_nce_loss(a, b, temp=0.07):
    a = F.normalize(a, dim=1)
    b = F.normalize(b, dim=1)

    logits = a @ b.T / temp
    labels = torch.arange(len(a), device=a.device)

    return F.cross_entropy(logits, labels)

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(" Device:", device)

    outfits = load_compatibility(COMPAT_FILE)
    dataset = PairDataset(outfits, DATA_ROOT)

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        drop_last=True,
        num_workers=2
    )

    model = ItemEncoder().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    best_loss = 1e9

    for epoch in range(EPOCHS):
        model.train()
        total = 0

        for img_a, img_b in tqdm(loader, desc=f"Epoch {epoch+1}"):
            img_a = img_a.to(device)
            img_b = img_b.to(device)

            emb_a = model(img_a)
            emb_b = model(img_b)

            loss = info_nce_loss(emb_a, emb_b)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total += loss.item()

        avg = total / len(loader)
        print(f" Epoch {epoch+1} loss = {avg:.4f}")

        if avg < best_loss:
            best_loss = avg
            os.makedirs("models", exist_ok=True)
            torch.save(model.state_dict(), MODEL_SAVE)
            print(" Saved best encoder")

    print(" Training done")

if __name__ == "__main__":
    main()
