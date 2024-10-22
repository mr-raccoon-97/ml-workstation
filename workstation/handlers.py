from workstation.repository import Repository
from workstation.callback import Callback
from workstation.publisher import Publisher
from workstation.session import Session
from workstation.commands import TrainModelTillEpoch

def handle_train_model_till_epoch(command: TrainModelTillEpoch, callback: Callback, publisher: Publisher, repository: Repository):
    model_type = repository.models.get(command.model.signature)
    criterion_type = repository.criterions.get(command.criterion.signature)
    optimizer_type = repository.optimizers.get(command.optimizer.signature)

    model = model_type(*command.model.args, **command.model.kwargs)
    criterion = criterion_type(*command.criterion.args, **command.criterion.kwargs)
    optimizer = optimizer_type(model.parameters(), *command.optimizer.args, **command.optimizer.kwargs)

    aggregate = repository.compiler.compile(model, criterion, optimizer)

    for iteration in command.iterations:
        dataset_type = repository.datasets.get(iteration.dataset.signature)
        repository.loaders.add(iteration.phase, dataset_type(*iteration.dataset.args, **iteration.dataset.kwargs),  **iteration.kwargs)

    epochs = 0
    with Session(aggregate, repository.loaders, repository, publisher) as session:
        while aggregate.epoch < command.epoch:
            aggregate.epoch += 1
            for phase, loader in repository.loaders:
                aggregate.phase = phase
                aggregate.iterate(loader, callback)
            epochs += 1
            if command.checkpoint and epochs % command.checkpoint == 0:
                session.commit()