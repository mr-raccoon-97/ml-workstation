from typing import Any
from typing import Callable
from collections import deque
from logging import getLogger
from workstation.publisher import Consumer as Base
from workstation.signals import Metric, Transaction

logger = getLogger(__name__)

def handle_metric(metric: Metric, buffer: deque[Metric]):
    buffer.append(metric)

def log_metric(metric: Metric):
    logger.info(f'*** End of phase {metric.phase} at epoch {metric.epoch} ***')
    logger.info(f'--- Publishing metric {metric.name}')
    logger.info(f'--- --- Batches: {metric.batch} ::: Value: {metric.value}')
    logger.info(f'-----------------------------------------------------------')

def handle_session(transaction: Transaction):
    logger.info(f'*** End of transaction ***')

class Consumer(Base):
    def __init__(self):
        super().__init__()
        self.buffer = deque[Metric]()
        self.history = list[Metric]()
        self.subscribe('metric', lambda metric: handle_metric(metric, self.buffer))
        self.subscribe('metric', log_metric)
        self.subscribe('session', handle_session)

    def begin(self):
        logger.info('*** Starting publisher')

    def commit(self):
        while self.buffer:
            metric = self.buffer.popleft()
            self.history.append(metric)
        logger.info('*** Commit transaction')

    def rollback(self):
        logger.info('*** Rollback transaction')
        self.buffer.clear()

    def close(self):
        logger.info('*** Closing publisher')