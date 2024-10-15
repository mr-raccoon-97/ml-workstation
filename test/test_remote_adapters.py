import pytest
from dataclasses import dataclass
from workstation.remote.adapters import Experiments, Models

@pytest.fixture
def experiments():
    return Experiments()

def test_experiments(experiments: Experiments):
    experiment = experiments.create('test')
    assert experiment.name == 'test'
    assert experiments.get(experiment.id) == experiment
    assert experiments.get_by_name('test') == experiment
    assert experiments.list() == [experiment]
    experiments.remove(experiment)
    assert experiments.get(experiment.id) is None
    assert experiments.get_by_name('test') is None
    assert experiments.list() == []

@dataclass
class Module:
    metadata: dict


def test_models(experiments: Experiments):
    try:
        experiment = experiments.create('test')
        module = Module(metadata={
            'name': 'test',
            'args': [1, 2, 3],
            'kwargs': {'a': 1, 'b': 2},
            'epochs': 10
        })
        models = Models(experiment)
        model = models.create(module)
        assert models.get(model.id) == model
        assert models.list() == [model]
        models.remove(model)
        assert models.get(model.id) is None
    finally:
        experiments.remove(experiment)