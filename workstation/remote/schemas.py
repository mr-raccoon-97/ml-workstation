from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

class Schema: ...

@dataclass
class Metric(Schema):
    name: str
    phase: str
    batch: int
    epoch: int
    value: float
    
@dataclass
class Experiment(Schema):
    id: UUID
    name: str

@dataclass
class Model(Schema):
    id: UUID
    name: str
    args: tuple
    kwargs: dict
    epochs: int
    
@dataclass
class Criterion(Schema):
    id: UUID
    name: str
    args: tuple
    kwargs: dict
    epochs: int

@dataclass
class Optimizer(Schema):
    id: UUID
    name: str
    args: tuple
    kwargs: dict
    epochs: int

@dataclass
class Dataset(Schema):
    id: UUID
    name: str
    args: tuple
    kwargs: dict

@dataclass
class Loader(Schema):
    id: UUID
    phase: str
    dataset: Dataset
    args: tuple
    kwargs: dict

@dataclass
class Session(Schema):
    id: UUID
    loaders: list[Loader]
    criterion: Criterion
    optimizer: Optimizer
    epochs: int
    start: datetime
    end: datetime