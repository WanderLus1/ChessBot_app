import torch.nn as nn

def create_model():
    return nn.Sequential(
        nn.Linear(147, 512),
        nn.ReLU(),

        nn.Linear(512, 512),
        nn.ReLU(),

        nn.Linear(512, 4096)
    )