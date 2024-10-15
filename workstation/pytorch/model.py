from typing import Literal
from torch import Tensor
from torch import inference_mode
from torch.nn import Module
from torch.optim import Optimizer
from workstation.protocols import Loader
from workstation.pytorch.settings import Settings
from workstation.callback import Callback

class Aggregate(Module):
    def __init__(self, model: Module, criterion: Module, optimizer: Optimizer, settings: Settings = None):
        super().__init__()
        self.settings = settings or Settings()
        self.device = self.settings.model.device
        self.epoch = 0
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
    
    @property
    def phase(self) -> Literal['train', 'evaluation']:
        return 'train' if self.training else 'evaluation'
    
    @phase.setter
    def phase(self, value: Literal['train', 'evaluation']):
        self.train() if value == 'train' else self.eval()
    
    def loss(self, output: Tensor, target: Tensor) -> Tensor:
        return self.criterion(output, target)
    
    def fit(self, input: Tensor, target: Tensor) -> tuple[Tensor, float]:
        self.optimizer.zero_grad()
        output = self.model(input)
        loss = self.loss(output, target)
        loss.backward()
        self.optimizer.step()
        return output, loss.item()
    
    @inference_mode()
    def evaluate(self, input: Tensor, target: Tensor) -> tuple[Tensor, float]:
        output = self.model(input)
        loss = self.loss(output, target)
        return output, loss.item()

    def forward(self, input: Tensor, target: Tensor) -> tuple[Tensor, float]:
        return self.fit(input, target) if self.training else self.evaluate(input, target)
    
    def iterate(self, loader: Loader, callback: Callback):
        callback.epoch = self.epoch
        callback.phase = self.phase
        for batch, (input, target) in enumerate(loader, start=1):
            input, target = input.to(self.device), target.to(self.device)
            output, loss = self(input, target)
            callback(batch, input, output, target, loss)
        callback.flush()