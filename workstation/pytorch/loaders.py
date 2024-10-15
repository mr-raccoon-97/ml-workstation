from typing import Optional
from typing import Literal
from workstation.protocols import Dataset
from workstation.aggregate import Loaders as Base
from workstation.pytorch.settings import Settings
from workstation.core.registry import Registry, register_loader
from workstation.pytorch.logging import on_loader_creation
from torch.utils.data import DataLoader as _DataLoader

INFRASTRUCTURE_PARAMETERS = {'dataset', 'pin_memory', 'pin_memory_device' ,'num_workers'}

class Loaders(Base):
    def __init__(self, settings: Settings = None, exclude_parameters: set[str] = INFRASTRUCTURE_PARAMETERS):
        super().__init__(Registry(exclude_parameters=exclude_parameters, excluded_positions=[0]))
        self.registry.register(_DataLoader)
        self.settings = settings or Settings()

    def add(self, phase: Literal['train', 'evaluation'], dataset: Dataset, batch_size: int, shuffle: bool, settings: Optional[Settings] = None):
        settings = settings or self.settings
        on_loader_creation(dataset)
        loader = _DataLoader(
            dataset=dataset, 
            batch_size=batch_size, 
            shuffle=shuffle, 
            pin_memory=settings.loaders.pin_memory, 
            pin_memory_device=settings.loaders.pin_memory_device,
            num_workers=settings.loaders.number_of_workers
        )
        register_loader(phase, loader)
        self.list.append((phase, loader))