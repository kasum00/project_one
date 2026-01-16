import os
import shutil
import random

SRC_ROOT = "data/Re-PolyVore"
OUT_ROOT = "data/cleaned_maryland_processed"
TRAIN_RATIO = 0.8
SEED = 42

random.seed(SEED)

CATEGORY_MAP = {
    "tops": ["top", "outerwear"],
    "bottoms": ["pants", "skirt", "legwear"],
    "dress": ["dress", "jumpsuit"],
    "shoes": ["shoes"],
    "bag": ["bag"],
    "accessories": ["bracelet", "brooch", "earrings", "necklace", "rings", "watches"],
    "others": ["hats", "eyewear", "gloves", "hairwear", "neckwear"],
}

def make_dirs():
    for split in ["train", "val"]:
        for cat in CATEGORY_MAP:
            os.makedirs(os.path.join(OUT_ROOT, split, cat), exist_ok=True)

def collect_images():
    samples = []

    for new_cat, old_cats in CATEGORY_MAP.items():
        for old_cat in old_cats:
            src_dir = os.path.join(SRC_ROOT, old_cat)
            if not os.path.isdir(src_dir):
                continue

            for fname in os.listdir(src_dir):
                if fname.lower().endswith((".jpg", ".png", ".jpeg")):
                    samples.append((new_cat, os.path.join(src_dir, fname)))

    return samples

def split_and_copy(samples):
    random.shuffle(samples)
    split_idx = int(len(samples) * TRAIN_RATIO)

    train_samples = samples[:split_idx]
    val_samples = samples[split_idx:]

    for split, data in [("train", train_samples), ("val", val_samples)]:
        for cat, src_path in data:
            dst_dir = os.path.join(OUT_ROOT, split, cat)
            shutil.copy(src_path, dst_dir)

if __name__ == "__main__":
    print("Building Cleaned Maryland dataset...")
    make_dirs()
    samples = collect_images()
    print(f"Total images found: {len(samples)}")
    split_and_copy(samples)
    print("Dataset build finished")
