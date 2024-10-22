from abc import ABC, abstractmethod
from typing import Protocol
from typing import Optional
from workstation.protocols import Module, Criterion, Optimizer, Dataset
from workstation.aggregate import Aggregate, Registry, Compiler, Loaders

class Weights[T: Module](ABC):

    @abstractmethod
    def store(self, module: T, folder: str | None = None) -> None: ...

    @abstractmethod
    def restore(self, module: T, folder: str | None = None) -> None: ...


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

    @abstractmethod
    def store(self, aggregate: Aggregate) -> None: ...

    @abstractmethod
    def restore(self, aggregate: Aggregate) -> None: ...