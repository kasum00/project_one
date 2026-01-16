import os, random
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class PairDataset(Dataset):
    def __init__(self, outfits, image_root):
        self.image_root = image_root
        self.pairs = []
        self.image_map = {}

        for root, _, files in os.walk(image_root):
            for f in files:
                if f.lower().endswith((".jpg", ".png", ".jpeg")):
                    key = os.path.splitext(f)[0]
                    self.image_map[key] = os.path.join(root, f)

        for items in outfits:
            valid = [i for i in items if i in self.image_map]
            for i in range(len(valid)):
                for j in range(i + 1, len(valid)):
                    self.pairs.append((valid[i], valid[j]))

        print(f"Images: {len(self.image_map)}")
        print(f"Positive pairs: {len(self.pairs)}")

        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        a, b = self.pairs[idx]
        pa = self.image_map[a]
        pb = self.image_map[b]

        img_a = self.transform(Image.open(pa).convert("RGB"))
        img_b = self.transform(Image.open(pb).convert("RGB"))

        return img_a, img_b
