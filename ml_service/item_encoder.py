import torch
import torch.nn as nn
from torchvision import models

class ItemEncoder(nn.Module):
    def __init__(self, embed_dim=256):
        super().__init__()
        base = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.DEFAULT
        )
        self.backbone = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(1280, embed_dim)

    def forward(self, x):
        x = self.backbone(x)
        x = self.pool(x).flatten(1)
        x = self.fc(x)
        return x  
