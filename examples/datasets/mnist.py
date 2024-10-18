from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor, Compose, Normalize
from torch.utils.data import Dataset

class Digits(Dataset):
    def __init__(self, train=True, normalize=True):
        self.transform = Compose([ToTensor(), Normalize((0.1307,), (0.3081,))]) if normalize else ToTensor()
        self.dataset = MNIST(root='data/datasets', train=train, download=True, transform=self.transform)

    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]