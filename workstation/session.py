from datetime import datetime, timezone
from workstation.aggregate import Aggregate, Loaders
from workstation.repository import Repository
from workstation.callback import Callback
from workstation.messages import Model, Transaction
from logging import getLogger

logger = getLogger(__name__)

class Session:
    def __init__(self, aggregate: Aggregate, loaders: Loaders, repository: Repository | None = None, callback: Callback | None = None):
        self.aggregate = aggregate
        self.loaders = loaders
        self.repository = repository
        self.callback = callback
        self.callback.setup(repository.folder)
        self.model = Model.create(self.aggregate)

    def begin(self):
        self.transaction = Transaction.create(self.aggregate, self.loaders)
        if self.callback:
            self.callback.begin()
            self.callback.deliver(self.model)
            self.aggregate.epoch = self.model.epochs

        if self.repository:
            if self.aggregate.epoch == 0:
                self.repository.store(self.aggregate)
            else:
                self.repository.restore(self.aggregate)

                
    def rollback(self):
        self.aggregate.epoch = self.model.epochs
        self.transaction = None
        if self.callback:
            self.callback.rollback()

        if self.repository:
            self.repository.restore(self.aggregate)
        

    def commit(self):
        self.transaction.end = datetime.now(timezone.utc)
        self.transaction.epochs = (self.model.epochs, self.aggregate.epoch)
        self.model.epochs = self.aggregate.epoch
        if self.callback:
            self.callback.deliver(self.transaction)
            self.callback.commit()

        if self.repository:
            self.repository.store(self.aggregate)
    
    def close(self):
        if self.callback:
            self.callback.close()

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