from uuid import UUID
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from datetime import datetime
from copy import deepcopy
from workstation.aggregate import Aggregate, Loader, Loaders

class Message: ...

@dataclass
class Metric(Message):
    name: str
    phase: str
    batch: int
    epoch: int
    value: float

@dataclass
class Model(Message):
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict
    epochs: int

    @staticmethod
    def create(aggregate: Aggregate):
        model = Model(
            signature=aggregate.model.metadata['signature'],
            hash=aggregate.model.metadata['hash'],
            name=aggregate.model.metadata['name'],
            args=aggregate.model.metadata['args'],
            kwargs=aggregate.model.metadata['kwargs'],
            epochs=aggregate.epoch
        )
        return deepcopy(model)

@dataclass
class Criterion(Message):
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict    

    @staticmethod
    def create(aggregate: Aggregate):
        if aggregate.criterion:
            criterion = Criterion(
                signature=aggregate.criterion.metadata['signature'],
                hash=aggregate.criterion.metadata['hash'],
                name=aggregate.criterion.metadata['name'],
                args=aggregate.criterion.metadata['args'],
                kwargs=aggregate.criterion.metadata['kwargs']
            )
        return deepcopy(criterion) if criterion else None


@dataclass
class Optimizer(Message):
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict

    @staticmethod
    def create(aggregate: Aggregate):
        if aggregate.optimizer:
            optimizer = Optimizer(
                signature=aggregate.optimizer.metadata['signature'],
                hash=aggregate.optimizer.metadata['hash'],
                name=aggregate.optimizer.metadata['name'],
                args=aggregate.optimizer.metadata['args'],
                kwargs=aggregate.optimizer.metadata['kwargs']
            ) 
        return deepcopy(optimizer) if optimizer else None

@dataclass
class Dataset(Message):
    signature: dict
    hash: str
    name: str
    args: tuple
    kwargs: dict

    @staticmethod
    def create(loader: Loader):
        loader = Dataset(
            signature=loader.metadata['signature'],
            hash=loader.metadata['dataset']['hash'],
            name=loader.metadata['dataset']['name'],
            args=loader.metadata['dataset']['args'],
            kwargs=loader.metadata['dataset']['kwargs']
        )
        return deepcopy(loader)

@dataclass
class Iteration(Message):
    phase: str
    dataset: Dataset
    kwargs: dict

    @staticmethod
    def create(phase: str, loader: Loader):
        return Iteration(
            phase=phase,
            dataset=Dataset.create(loader),
            kwargs=loader.metadata['kwargs']
        )

@dataclass
class Transaction(Message):
    epochs: tuple[int, int]
    start: datetime
    end: datetime
    criterion: Optional[Criterion]
    optimizer: Optional[Optimizer]
    iterations: list[Iteration]

    @staticmethod
    def create(aggregate: Aggregate, loaders: Loaders):
        return Transaction(
            epochs=None,
            start=datetime.now(),
            end=None,
            criterion=Criterion.create(aggregate),
            optimizer=Optimizer.create(aggregate),
            iterations=[Iteration.create(phase, loader) for phase, loader in loaders]
        )