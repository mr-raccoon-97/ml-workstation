from datetime import datetime
from workstation.core.registry import encode
from workstation.protocols import Module, Dataset
from workstation.aggregate import Loaders, Aggregate
from workstation.publisher import Publisher
from workstation.repository import Repository
from workstation.core.registry import serialize

class Session:
    def __init__(self, aggregate: Aggregate, loaders: Loaders, publisher: Publisher = None, repository: Repository | None = None):
        self.aggregate = aggregate
        self.loaders = loaders
        self.start = None
        self.end = None
        self.publisher = publisher or Publisher()
        self.repository = repository
        
    def begin(self):
        self.start = datetime.now()
        self.publisher.begin()

    def commit(self):
        self.end = datetime.now()
        if self.repository is not None:
            self.repository.store(self.aggregate)

        self.publisher.publish('model', serialize(self.aggregate.model))
        self.publisher.publish('session', encode({
            'criterion': serialize(self.aggregate.criterion),
            'optimizer': serialize(self.aggregate.optimizer),
            'loaders': [serialize(loader) for _, loader in self.loaders],
            'start': self.start,
            'end': self.end,
        }))
        self.publisher.commit()

    def rollback(self):
        self.start = None
        self.end = None
        self.publisher.rollback()
        if self.repository is not None:
            self.repository.restore(self.aggregate)

    def close(self):
        self.publisher.close()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()        

    def __enter__(self):
        self.begin()
        return self


from torch import Tensor
from torch.nn import Module, Linear, Dropout, Flatten
from torch.nn import ReLU

class MLP(Module):
    def __init__(self, input_dimension: int, hidden_dimension: int, output_dimension: int, p: float):
        super().__init__()
        self.flatten = Flatten(start_dim=1)
        self.activation = ReLU()
        self.dropout = Dropout(p)
        self.input_layer = Linear(input_dimension, hidden_dimension)
        self.output_layer = Linear(hidden_dimension, output_dimension)

    def forward(self, sequence: Tensor) -> Tensor:
        sequence = self.input_layer(sequence.flatten(1))
        sequence = self.activation(sequence)
        sequence = self.dropout(sequence)
        return self.output_layer(sequence)
    
from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor, Compose, Normalize
from torch.utils.data import Dataset
from torch.optim import Adam
from torch.nn import CrossEntropyLoss

class Digits(Dataset):
    def __init__(self, train: bool = True, normalize: bool = True):
        self.transform = Compose([ToTensor(), Normalize((0.1307,), (0.3081,))]) if normalize else ToTensor()
        self.dataset = MNIST(root='data/datasets', train=train, download=True, transform=self.transform)

    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self, idx):
        return self.dataset[idx]
    

from workstation.pytorch.repository import Repository
from workstation.pytorch.model import Aggregate
from workstation.pytorch.loaders import Loaders

Repository.models.register(MLP)
Repository.criterions.register(CrossEntropyLoss)
Repository.optimizers.register(Adam)
Repository.datasets.register(Digits)


aggregate = Aggregate(
    model=MLP(784, 128, 10, 0.5),
    criterion=CrossEntropyLoss(),
    optimizer=Adam(MLP(784, 128, 10, 0.5).parameters())
)

loaders = Loaders()
loaders.add('train', Digits(train=True), batch_size=32, shuffle=True)
loaders.add('test', Digits(train=False), batch_size=32, shuffle=False)

session = Session(aggregate, loaders, None)