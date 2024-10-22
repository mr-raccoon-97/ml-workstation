from abc import ABC, abstractmethod
from dataclasses import dataclass
from workstation.messages import Model, Criterion, Optimizer, Iteration
from workstation.repository import Repository
from workstation.callback import Callback
from workstation.session import Session

class Command(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs): ...

@dataclass
class TrainModelTillEpoch(Command):
    epoch: int
    model: Model
    criterion: Criterion
    optimizer: Optimizer
    iterations: list[Iteration]
    checkpoint: int = None

    def execute(self, callback: Callback, repository: Repository):
        model_type, _ = repository.models.get(self.model.signature)
        criterion_type, _  = repository.criterions.get(self.criterion.signature)
        optimizer_type, _  = repository.optimizers.get(self.optimizer.signature)

        model = model_type(*self.model.args, **self.model.kwargs)
        criterion = criterion_type(*self.criterion.args, **self.criterion.kwargs)
        optimizer = optimizer_type(model.parameters(), *self.optimizer.args, **self.optimizer.kwargs)

        aggregate = repository.compiler.compile(model, criterion, optimizer)
        loaders = repository.loaders

        for iteration in self.iterations:
            dataset_type = repository.datasets.get(iteration.dataset.signature)
            loaders.add(iteration.phase, dataset_type(*iteration.dataset.args, **iteration.dataset.kwargs),  **iteration.kwargs)

        epochs = 0
        with Session(aggregate, loaders, repository, callback) as session:
            while aggregate.epoch < self.epoch:
                aggregate.epoch += 1
                for phase, loader in loaders:
                    aggregate.phase = phase
                    aggregate.iterate(loader, callback)

                epochs += 1
                if self.checkpoint and epochs % self.checkpoint == 0:
                    session.commit()