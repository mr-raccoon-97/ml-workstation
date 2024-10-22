from uuid import UUID
from requests import get, post, delete
from typing import Optional
from dataclasses import dataclass
from msgspec.json import encode
from workstation.remote.settings import Settings

@dataclass
class Experiment:
    id: UUID
    name: str

@dataclass
class Model:
    id: UUID
    signature: UUID
    hash: str
    name: str
    args: tuple
    kwargs: dict
    epochs: int

class Experiments:

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

    def create(self, name: str) -> Experiment:
        response = post(f'{self.settings.backend.uri}/experiments/', json={'name': name})
        response.raise_for_status()
        return Experiment(**response.json())
    
    def get(self, name: str) -> Optional[Experiment]:
        response = get(f'{self.settings.backend.uri}/experiments?name={name}')
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Experiment(**response.json())
    
    def list(self) -> list[Experiment]:
        response = get(f'{self.settings.backend.uri}/experiments/')
        response.raise_for_status()
        return [Experiment(**experiment) for experiment in response.json()]

    def remove(self, experiment: Experiment):
        response = delete(f'{self.settings.backend.uri}/experiments/{experiment.id}/')
        response.raise_for_status()

    
class Models:
    
    def __init__(self, experiment: Experiment, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.experiment = experiment    

    def create(self, model: Model) -> Model:
        response = post(f'{self.settings.backend.uri}/experiments/{self.experiment.id}/models/', data=encode(model))
        response.raise_for_status()
        return Model(**response.json())

    def get(self, hash: str) -> Optional[Model]:
        response = get(f'{self.settings.backend.uri}/experiments/{self.experiment.id}/models/{hash}/')
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Model(**response.json())