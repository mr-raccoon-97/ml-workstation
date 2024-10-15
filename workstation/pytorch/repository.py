from workstation.core.registry import Registry
from workstation.repository import Repository as Base
from workstation.pytorch.settings import Settings
from workstation.pytorch.compiler import Compiler
from workstation.pytorch.loaders import Loaders

class Repository(Base):
    models = Registry(aditional_parameters={'epochs': 0})
    criterions = Registry()
    optimizers = Registry(excluded_positions=[0], exclude_parameters={'params'})
    datasets = Registry(exclude_parameters={'root', 'download'})

    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.compiler = Compiler(self.settings)
        self.loaders = Loaders(self.settings)