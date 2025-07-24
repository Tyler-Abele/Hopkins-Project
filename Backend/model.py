import torch
import torch.nn as nn
import torchvision.models as models
from model import HypernasalityDetectorResNet18

class HypernasalityDetectorResNet18(nn.Module):
    def __init__(self, num_classes = 2):
        super(HypernasalityDetectorResNet18, self).__init__()

        self.resnet18 = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        
    def forward(self, x):
        return self.model(x)

if __name__ == '__main__':
    dummy_input = torch.randn(1, 3, 224, 224)  # Example input
    model = HypernasalityDetectorResNet18(num_classes=2)
    model.eval()
    
    with torch.no_grad():
        output = model(dummy_input)
    
    print(f"Model output shape: {output.shape}")
    print("Model created successfully")