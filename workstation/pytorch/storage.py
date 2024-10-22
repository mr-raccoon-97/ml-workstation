from os import makedirs
from os import path, makedirs
from logging import getLogger
from typing import Optional

from torch import save, load
from torch.nn import Module

from workstation.protocols import Criterion, Optimizer
from workstation.repository import Storage as Base
from workstation.pytorch.settings import Settings
from workstation.pytorch.logging import on_restoring, on_storing

logger = getLogger(__name__)

class Weights[T: Module]:
    def __init__(self, directory: str):
        self.location = directory
        if not path.exists(self.location):
            makedirs(self.location)
    
    def store(self, module: T, folder: str, name: Optional[str] = None):
        filename = name + '-' + module.metadata['hash'] if name else module.metadata['hash']
        location = path.join(self.location, folder)
        on_storing(module, location)
        save(module.state_dict(), path.join(location, filename + '.pth'))
        
    def restore(self, module: T, folder: str, name: Optional[str] = None):
        filename = name + module.metadata['hash'] if name else module.metadata['hash']
        location = path.join(self.location, folder, filename)
        try:
            on_restoring(module, location)
            state_dict = load(path.join(location, filename + '.pth'), weights_only=False)
            module.load_state_dict(state_dict)
        except FileNotFoundError as error:
            logger.warning(f'ERROR RESTORING WEIGHTS: {error}')
        except Exception as error:
            logger.error(f'ERROR RESTORING WEIGHTS: {error}')
            raise error

    
class Storage(Base):
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.directory = self.settings .weights.directory
        if not path.exists(self.directory):
            makedirs(self.directory)
        self.models = Weights[Module](self.directory)
        self.optimizers = Weights[Optimizer](self.directory)
        self.criterions = Weights[Criterion](self.directory)