import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from tqdm import tqdm

# =====================
# CONFIG
# =====================
DATA_DIR = "data/cleaned_maryland_processed"
BATCH_SIZE = 32
EPOCHS = 30
LR = 1e-4
MODEL_OUT = "ml_models/category_classifier.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =====================
# TRAIN FUNCTION
# =====================
def main():
    print("Using device:", DEVICE)

    # -----------------
    # TRANSFORMS
    # -----------------
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    val_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # -----------------
    # DATASET
    # -----------------
    train_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "train"), transform=train_tf)
    val_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "val"), transform=val_tf)

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=4,          # Windows OK
        pin_memory=(DEVICE.type == "cuda")
    )

    val_loader = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=(DEVICE.type == "cuda")
    )

    num_classes = len(train_ds.classes)
    print("Classes:", train_ds.classes)

    # -----------------
    # MODEL
    # -----------------
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    scaler = torch.amp.GradScaler("cuda") if DEVICE.type == "cuda" else None

    best_acc = 0.0

    # -----------------
    # TRAIN LOOP
    # -----------------
    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch+1}/{EPOCHS}")

        # ---- TRAIN ----
        model.train()
        correct, total = 0, 0

        for x, y in tqdm(train_loader, desc="Train"):
            x = x.to(DEVICE)
            y = y.to(DEVICE)

            optimizer.zero_grad()

            if DEVICE.type == "cuda":
                with torch.autocast("cuda"):
                    out = model(x)
                    loss = criterion(out, y)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
            else:
                out = model(x)
                loss = criterion(out, y)
                loss.backward()
                optimizer.step()

            pred = out.argmax(1)
            correct += (pred == y).sum().item()
            total += y.size(0)

        train_acc = correct / total

        # ---- VAL ----
        model.eval()
        correct, total = 0, 0

        with torch.no_grad():
            for x, y in tqdm(val_loader, desc="Val"):
                x = x.to(DEVICE)
                y = y.to(DEVICE)

                out = model(x)
                pred = out.argmax(1)
                correct += (pred == y).sum().item()
                total += y.size(0)

        val_acc = correct / total
        print(f"Train acc: {train_acc:.4f} | Val acc: {val_acc:.4f}")

        if val_acc > best_acc:
            best_acc = val_acc
            os.makedirs("models", exist_ok=True)
            torch.save(model.state_dict(), MODEL_OUT)
            print(" Saved best model")

    print("\n Classifier training finished")
    print("Best val acc:", best_acc)


# =====================
# ENTRY POINT (WINDOWS FIX)
# =====================
if __name__ == "__main__":
    main()
