from logging import getLogger
from pika import BasicProperties
from pika import BlockingConnection, ConnectionParameters
from pika.connection import Connection
from msgspec.json import encode
from workstation.publisher import Consumer as Base
from workstation.signals import Metric, Model, Transaction
from workstation.remote.adapters import Experiments, Models
from workstation.remote.settings import Settings

logger = getLogger(__name__)

class Consumer(Base):
    def __init__(self, connection: Connection, settings: Settings = None):
        super().__init__()
        self.connection = connection
        self.settings = settings or Settings()
        self.experiments = Experiments(self.settings)
        self.subscribe(Model, self.handle_model)
        self.subscribe(Metric, self.handle_metric)
        self.subscribe(Transaction, self.handle_transaction)
        self.subscribe(Transaction, self.update_model)

    def name(self, experiment_name: str):
        self.experiment = self.experiments.get(experiment_name)
        if not self.experiment:
            self.experiment = self.experiments.create(experiment_name)
        self.models = Models(self.experiment, self.settings)

    def handle_model(self, model: Model):
        self.model = self.models.get(model.hash)
        if not self.model:
            self.model = self.models.create(model)
        else:
            model.epochs = self.model.epochs        

    def handle_metric(self, metric: Metric):
        assert self.model is not None
        self.channel.basic_publish(
            exchange=self.settings.rabbitmq.exchange,
            routing_key='metrics',
            body=encode(metric),
            properties=BasicProperties(
                headers={
                    'X-Resource-ID': self.model.id,
                }
            )
        )

    def handle_transaction(self, transaction: Transaction):
        assert self.model is not None        
        self.channel.basic_publish(
            exchange=self.settings.rabbitmq.exchange,
            routing_key='transaction',
            body=encode(transaction),
            properties=BasicProperties(
                headers={
                    'X-Resource-ID': self.model.id,
                }
            )
        )

    def update_model(self, transaction: Transaction):
        assert self.model is not None
        self.model.epochs += transaction.epochs[1] - transaction.epochs[0]
        self.channel.basic_publish(
            exchange=self.settings.rabbitmq.exchange,
            routing_key='models',
            body=encode(self.model),
            properties=BasicProperties(
                headers={
                    'X-Resource-ID': self.experiment.id,
                }
            )
        )

    def begin(self):
        self.channel = self.connection.channel()
        self.channel.tx_select()

    def commit(self):
        logger.info('--- Committing RabbitMQ Publisher Transaction ---')
        self.channel.tx_commit()

    def rollback(self):
        logger.info('--- Rolling back RabbitMQ Publisher Transaction ---')
        self.channel.tx_rollback()

    def close(self):
        self.channel.close()
        logger.info('--- Closing RabbitMQ Publisher Transaction ---')


class RabbitMQ:
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
    
    def connect(self):
        self.connection = BlockingConnection(ConnectionParameters(
            host=self.settings.rabbitmq.host, 
            port=self.settings.rabbitmq.port)
        )
    
    def close(self):
        self.connection.close()

    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()