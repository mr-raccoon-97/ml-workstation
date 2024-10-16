from uuid import UUID
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
from datetime import datetime
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
        return Model(
            hash=aggregate.model.metadata['hash'],
            name=aggregate.model.metadata['name'],
            args=aggregate.model.metadata['args'],
            kwargs=aggregate.model.metadata['kwargs'],
            epochs=aggregate.epoch
        )

@dataclass
class Criterion(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict    

    @staticmethod
    def create(aggregate: Aggregate):
        return Criterion(
            hash=aggregate.criterion.metadata['hash'],
            name=aggregate.criterion.metadata['name'],
            args=aggregate.criterion.metadata['args'],
            kwargs=aggregate.criterion.metadata['kwargs']
        ) if aggregate.criterion else None


@dataclass
class Optimizer(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict

    @staticmethod
    def create(aggregate: Aggregate):
        return Optimizer(
            hash=aggregate.optimizer.metadata['hash'],
            name=aggregate.optimizer.metadata['name'],
            args=aggregate.optimizer.metadata['args'],
            kwargs=aggregate.optimizer.metadata['kwargs']
        ) if aggregate.optimizer else None

@dataclass
class Dataset(Signal):
    hash: str
    name: str
    args: tuple
    kwargs: dict

    @staticmethod
    def create(loader: Loader):
        return Dataset(
            hash=loader.metadata['dataset']['hash'],
            name=loader.metadata['dataset']['name'],
            args=loader.metadata['dataset']['args'],
            kwargs=loader.metadata['dataset']['kwargs']
        )

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
            kwargs=loader.metadata['loader']['kwargs']
        )

@dataclass
class Transaction(Signal):
    epochs: tuple[int, int]
    duration: tuple[datetime, datetime]
    model: Model
    criterion: Optional[Criterion]
    optimizer: Optional[Optimizer]
    iterations: list[Iteration]

    @staticmethod
    def create(aggregate: Aggregate, loaders: Loaders):
        return Transaction(
            epochs=(aggregate.epoch, aggregate.epoch),
            duration=(datetime.now(), datetime.now()),
            model=Model.create(aggregate),
            criterion=Criterion.create(aggregate),
            optimizer=Optimizer.create(aggregate),
            iterations=[Iteration.create(phase, loader) for phase, loader in loaders]
        )