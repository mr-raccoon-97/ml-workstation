from typing import Any
from typing import Callable
from collections import deque
from logging import getLogger
from workstation.publisher import Consumer as Base
from workstation.messages import Metric, Model, Transaction

logger = getLogger(__name__)

def handle_metric(metric: Metric, buffer: deque[Metric]):
    buffer.append(metric)

def log_metric(metric: Metric):
    logger.info(f'*** End of phase {metric.phase} at epoch {metric.epoch} ***')
    logger.info(f'--- Publishing metric {metric.name}')
    logger.info(f'--- --- Batches: {metric.batch} ::: Value: {metric.value}')
    logger.info(f'-----------------------------------------------------------')
    
def handle_transaction(transaction: Transaction, transactions: list[Transaction], model: Model):
    logger.info(f'*** End of transaction {transaction} ***')
    transactions.append(transaction)

def update_model(transaction: Transaction, model: Model):
    logger.info(f'*** Updating model with epochs {model.epochs} ***')
    

class Consumer(Base):
    def __init__(self):
        super().__init__()
        self.buffer = deque[Metric]()
        self.history = list[Metric]()
        self.transactions = list[Transaction]()
        self.subscribe(Metric, lambda metric: handle_metric(metric, self.buffer))
        self.subscribe(Metric, log_metric)
        self.subscribe(Model, self.handle_model)
        self.subscribe(Transaction, lambda transaction: handle_transaction(transaction, self.transactions, self.model))
        self.subscribe(Transaction, lambda transaction: update_model(transaction, self.model))

    def handle_model(self, model: Model):
        self.model = model

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