from workstation.registry import Registry
from workstation.repository import Repository as Base
from workstation.pytorch.settings import Settings
from workstation.pytorch.compiler import Compiler
from workstation.pytorch.loaders import Loaders
from workstation.pytorch.storage import Storage
from workstation.aggregate import Aggregate

class Repository(Base):
    models = Registry()
    criterions = Registry()
    optimizers = Registry(excluded_positions=[0], exclude_parameters={'params'})
    datasets = Registry(exclude_parameters={'root', 'download'})

    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.storage = Storage(self.settings)
        self.compiler = Compiler(self.settings)
        self.loaders = Loaders(self.settings)
        self.folder = 'default'

    def store(self, aggregate: Aggregate):
        self.storage.models.store(aggregate.model, self.folder)
        self.storage.optimizers.store(aggregate.optimizer, self.folder)
        self.storage.criterions.store(aggregate.criterion, self.folder)

    def restore(self, aggregate: Aggregate):
        self.storage.models.restore(aggregate.model, self.folder)
        self.storage.optimizers.restore(aggregate.optimizer, self.folder)
        self.storage.criterions.restore(aggregate.criterion, self.folder)