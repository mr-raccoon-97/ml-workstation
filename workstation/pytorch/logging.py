from os import makedirs
from os import path, makedirs
from logging import getLogger
from workstation.protocols import Module, Loader, Dataset
from workstation.protocols import Criterion, Optimizer
from workstation.aggregate import Aggregate

logger = getLogger(__name__)

def on_storing(module: Module, location: str):
    logger.info(f'*** Saving weights for module {module.metadata["name"]}')
    logger.info(f'--- On location {location}')
    if not path.exists(location):
        makedirs(location)
   
def on_restoring(module: Module, location: str):
    logger.info(f'*** Restoring weights for module {module.metadata["name"]}')
    logger.info(f'--- From location {location}')
    if not path.exists(location):
        raise FileNotFoundError(f'WEIGHTS NOT FOUND ON {location}')
    
def on_loader_creation(dataset: Dataset):
    logger.info(f'*** Creating loader for dataset {dataset.metadata["name"]}')
    logger.info(f'--- With lenght: {len(dataset)}')

def on_compiling(model: Module, criterion: Criterion, optimizer: Optimizer):
    logger.info(f'*** Compiling')
    logger.info(f'--- With Model: {model.metadata["name"]}')
    logger.info(f'--- With Criterion: {criterion.metadata["name"]}')
    logger.info(f'--- With Optimizer: {optimizer.metadata["name"]}')

def on_compiled(aggregate: Aggregate):
    logger.info(f'*** Model compiled successfully')
    logger.info(f'--- {aggregate}')

def on_call(metric: str, batch: int, value: float, phase: str, epoch: int):
    if batch % 100 == 0:
        logger.info(f'*** Metric {metric} on phase {phase} at epoch {epoch}')
        logger.info(f'--- Batch: {batch} ::: Value: {value}')

def on_update(metric: str, batch: int, phase: str, value: float):
    logger.info(f'::: End of phase {phase} average {metric} on {batch} batches: {value:.4f}')

def on_reset(metric: str, epoch: int, value: float):
    logger.info(f'--- End of epoch {epoch} average {metric}: {value:.4f}')