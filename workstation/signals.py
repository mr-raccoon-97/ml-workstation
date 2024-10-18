from uuid import UUID
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from datetime import datetime
from copy import deepcopy
from workstation.aggregate import Aggregate, Loader, Loaders

class Signal: ...

@dataclass
class Metric(Signal):
    name: str
    phase: str
    batch: int
    epoch: int
    value: float

@dataclass
class Model(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict
    epochs: int

    @staticmethod
    def create(aggregate: Aggregate):
        model = Model(
            hash=aggregate.model.metadata['hash'],
            name=aggregate.model.metadata['name'],
            args=aggregate.model.metadata['args'],
            kwargs=aggregate.model.metadata['kwargs'],
            epochs=aggregate.epoch
        )
        return deepcopy(model)

@dataclass
class Criterion(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict    

    @staticmethod
    def create(aggregate: Aggregate):
        if aggregate.criterion:
            criterion = Criterion(
                hash=aggregate.criterion.metadata['hash'],
                name=aggregate.criterion.metadata['name'],
                args=aggregate.criterion.metadata['args'],
                kwargs=aggregate.criterion.metadata['kwargs']
            )
        return deepcopy(criterion) if criterion else None


@dataclass
class Optimizer(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict

    @staticmethod
    def create(aggregate: Aggregate):
        if aggregate.optimizer:
            optimizer = Optimizer(
                hash=aggregate.optimizer.metadata['hash'],
                name=aggregate.optimizer.metadata['name'],
                args=aggregate.optimizer.metadata['args'],
                kwargs=aggregate.optimizer.metadata['kwargs']
            ) 
        return deepcopy(optimizer) if optimizer else None

@dataclass
class Dataset(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict

    @staticmethod
    def create(loader: Loader):
        loader = Dataset(
            hash=loader.metadata['dataset']['hash'],
            name=loader.metadata['dataset']['name'],
            args=loader.metadata['dataset']['args'],
            kwargs=loader.metadata['dataset']['kwargs']
        )
        return deepcopy(loader)

@dataclass
class Iteration(Signal):
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
class Transaction(Signal):
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