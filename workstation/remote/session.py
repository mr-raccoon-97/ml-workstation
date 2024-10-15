from datetime import datetime
from workstation.core.registry import encode
from workstation.aggregate import Loaders, Aggregate
from workstation.publisher import Publisher
from workstation.repository import Repository
from workstation.core.registry import serialize

class Session:
    def __init__(self, aggregate: Aggregate, loaders: Loaders, publisher: Publisher = None, repository: Repository | None = None):
        self.aggregate = aggregate
        self.loaders = loaders
        self.start = None
        self.end = None
        self.publisher = publisher or Publisher()
        self.repository = repository
        self.epochs = 0
        
    def begin(self):
        self.start = datetime.now()
        self.publisher.begin()

    def commit(self):
        self.end = datetime.now()
        if self.repository is not None:
            self.repository.store(self.aggregate)

        self.publisher.publish('model', serialize(self.aggregate.model))
        self.publisher.publish('session', encode({
            'criterion': serialize(self.aggregate.criterion),
            'optimizer': serialize(self.aggregate.optimizer),
            'epochs': self.epochs,
            'loaders': [serialize(loader) for _, loader in self.loaders],
            'start': self.start,
            'end': self.end,
        }))
        self.publisher.commit()

    def rollback(self):
        self.start = None
        self.end = None
        self.publisher.rollback()
        if self.repository is not None:
            self.repository.restore(self.aggregate)

    def close(self):
        self.publisher.close()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()        

    def __enter__(self):
        self.begin()
        return self
