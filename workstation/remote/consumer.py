from logging import getLogger
from pika import BasicProperties
from pika import BlockingConnection, ConnectionParameters
from pika.channel import Channel
from pika.connection import Connection

from workstation.publisher import Consumer as Base
from workstation.remote.schemas import Metric, Session, Model
from workstation.remote.settings import Settings
from workstation.core.registry import encode

logger = getLogger(__name__)

def handle_model(model: Model, channel: Channel, settings: Settings):
    channel.basic_publish(
        exchange='',
        routing_key='models',
        body=encode(model)
    )

def handle_metric(metric: Metric, model: Model, channel: Channel, settings: Settings):
    channel.basic_publish(
        exchange='',
        routing_key='metrics',
        body=encode(metric),
        properties=BasicProperties(
            headers={
                'X-Resource-ID': str(model.id)
            }
        )
    )

def handle_session(session: Session, model: Model, channel: Channel, settings: Settings):
    channel.basic_publish(
        exchange='',
        routing_key='sessions',
        body=encode(session),
        properties=BasicProperties(
            headers={
                'X-Resource-ID': str(model.id)
            }
        )
    )

class Consumer(Base):
    def __init__(self, model: Model, connection: Connection, settings: Settings = None):
        super().__init__()
        self.connection = connection
        self.settings = settings or Settings()
        self.model = model

    def begin(self):
        self.channel = self.connection.channel()
        self.subscribe('model', lambda model: handle_model(model, self.channel, self.settings))
        self.subscribe('metric', lambda metric: handle_metric(metric, self.model, self.channel, self.settings))
        self.subscribe('session', lambda session: handle_session(session, self.model, self.channel, self.settings))
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
        self.handlers.clear()


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