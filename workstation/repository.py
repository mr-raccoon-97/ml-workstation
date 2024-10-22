from os import path
from abc import ABC, abstractmethod
from typing import Protocol
from typing import Optional
from workstation.protocols import Module, Criterion, Optimizer, Dataset
from workstation.aggregate import Aggregate, Registry, Compiler, Loaders

class Weights[T: Module](ABC):

    @abstractmethod
    def store(self, module: T, folder: str, name: Optional[str]) -> None: ...

    @abstractmethod
    def restore(self, module: T, folder: str, name: Optional[str]) -> None: ...


class Storage(Protocol):
    models: Weights[Module]
    criterions: Optional[Weights[Criterion]]
    optimizers: Optional[Weights[Optimizer]]


class Repository(ABC):
    models: Registry[Module]
    datasets: Registry[Dataset]
    criterions: Optional[Registry[Criterion]]
    optimizers: Optional[Registry[Optimizer]]
    loaders: Loaders
    storage: Storage
    compiler: Compiler
    
    def __init__(self, folder: str = 'default'):
        self.folder = folder

    def store(self, aggregate: Aggregate):
        self.storage.models.store(aggregate.model, path.join(self.folder, aggregate.model.metadata['hash']), 'model')   
        self.storage.optimizers.store(aggregate.optimizer, path.join(self.folder, aggregate.model.metadata['hash']), 'optimizer')
        self.storage.criterions.store(aggregate.criterion, path.join(self.folder, aggregate.model.metadata['hash']), 'criterion')

    def restore(self, aggregate: Aggregate):
        self.storage.models.restore(aggregate.model, path.join(self.folder, aggregate.model.metadata['hash']), 'model')
        self.storage.optimizers.restore(aggregate.optimizer, path.join(self.folder, aggregate.model.metadata['hash']), 'optimizer')
        self.storage.criterions.restore(aggregate.criterion, path.join(self.folder, aggregate.model.metadata['hash']), 'criterion')