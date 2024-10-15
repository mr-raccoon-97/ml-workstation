from uuid import UUID
from requests import get, post, delete
from typing import Optional

from workstation.remote.schemas import Experiment
from workstation.remote.settings import Settings
from workstation.protocols import Module
from workstation.core.registry import serialize
from workstation.remote.schemas import Model, Experiment


class Experiments:

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

    def create(self, name: str) -> Experiment:
        response = post(f'{self.settings.backend.uri}/experiments/', json={'name': name})
        response.raise_for_status()
        return Experiment(**response.json())

    def get(self, id: UUID) -> Optional[Experiment]:
        response = get(f'{self.settings.backend.uri}/experiments/{id}')
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Experiment(**response.json())
    
    def get_by_name(self, name: str) -> Optional[Experiment]:
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

    def create(self, model: Module) -> Model:
        response = post(f'{self.settings.backend.uri}/experiments/{self.experiment.id}/models/', data=serialize(model))
        response.raise_for_status()
        return Model(**response.json())
    
    def list(self) -> list[Model]:
        response = get(f'{self.settings.backend.uri}/experiments/{self.experiment.id}/models/')
        response.raise_for_status()
        return [Model(**model) for model in response.json()]

    def get(self, id: UUID) -> Optional[Model]:
        response = get(f'{self.settings.backend.uri}/models/{id}/')
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return Model(**response.json())
    
    def remove(self, model: Model):
        response = delete(f'{self.settings.backend.uri}/models/{model.id}/')
        response.raise_for_status()