from pydantic import Field
from pydantic_settings import BaseSettings


class RabbitMQSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=5672)
    
    @property
    def uri(self) -> str:
        return f'amqp://{self.host}:{self.port}'
    

class BackendSettings(BaseSettings):
    host: str = Field(default='localhost')
    port: int = Field(default=8000)

    @property
    def uri(self) -> str:
        return f'http://{self.host}:{self.port}'
    

class Settings(BaseSettings):
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    backend: BackendSettings = Field(default_factory=BackendSettings)