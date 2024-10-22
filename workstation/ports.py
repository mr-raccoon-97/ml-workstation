from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from dataclasses import dataclass

@dataclass
class Experiment:
    id: UUID
    name: str

@dataclass
class Model:
    id: UUID
    hash: str
    name: str
    args: tuple
    kwargs: dict
    epochs: int

class Experiments:

    @abstractmethod
    def create(self, name: str) -> Experiment: ...
    
    def get(self, name: str) -> Optional[Experiment]: ...
    
    def list(self) -> list[Experiment]: ...

    
class Models:

    def create(self, model: Model) -> Model: ...

    def get(self, hash: str) -> Optional[Model]: ...