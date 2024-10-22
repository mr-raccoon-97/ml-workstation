from os import path
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

    def __init__(self, experiment_name: str = None, settings: Settings = None):
        super().__init__(experiment_name or 'default')
        self.settings = settings or Settings()
        self.storage = Storage(self.settings)
        self.compiler = Compiler(self.settings)
        self.loaders = Loaders(self.settings)