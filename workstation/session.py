from workstation.aggregate import Aggregate, Loaders
from workstation.repository import Repository
from workstation.publisher import Publisher
from workstation.signals import Model, Transaction
from logging import getLogger

logger = getLogger(__name__)

class Session:
    def __init__(self, aggregate: Aggregate, loaders: Loaders, repository: Repository | None = None, publisher: Publisher | None = None):
        self.aggregate = aggregate
        self.loaders = loaders
        self.repository = repository
        self.epoch = aggregate.epoch
        self.publisher = publisher
    
    def begin(self):
        self.transaction = Transaction.create(self.aggregate, self.loaders)
        if self.repository:
            self.repository.store(self.aggregate)
        if self.publisher:
            self.publisher.begin()
            self.publisher.publish(Model.create(self.aggregate))

    def rollback(self):
        self.transaction = None
        if self.repository:
            self.repository.restore(self.aggregate)
        self.aggregate.epoch = self.epoch

    def commit(self):
        self.transaction.epochs = (self.epoch, self.aggregate.epoch)
        self.epoch = self.aggregate.epoch
        if self.publisher:
            self.publisher.publish(self.transaction)
            self.publisher.commit()

        if self.repository:
            self.repository.store(self.aggregate)
    
    def close(self):
        if self.publisher:
            self.publisher.close()

    def __enter__(self):
        self.begin()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            logger.error(f'ERROR: {exc_value}')
            self.rollback()
        else:
            self.commit()
        self.close()