from workstation.protocols import Module, Criterion, Optimizer
from workstation.pytorch.model import Aggregate
from workstation.pytorch.settings import Settings
from workstation.pytorch.logging import on_compiling, on_compiled
from logging import getLogger

logger = getLogger(__name__)

class Compiler:
    def __init__(self, settings: Settings = None) -> None:
        self.settings = settings or Settings()
        self.raise_on_error = self.settings.compilation.raise_on_error
        self.device = self.settings.model.device

    def compile(self, model: Module, criterion: Criterion, optimizer: Optimizer) -> Aggregate:
        on_compiling(model, criterion, optimizer)
        aggregate = Aggregate(model, criterion, optimizer, self.settings).to(self.device)
        try:
            aggregate.compile()
            on_compiled(aggregate)
            logger.info(f'On device: {self.device}')
            return aggregate
        except Exception as error:
            if self.raise_on_error:
                raise error
            else:
                logger.error(error)
                logger.warning(f'RETURNING UNCOMPILED MODEL')
                return aggregate