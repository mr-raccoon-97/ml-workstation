from abc import ABC, abstractmethod
from typing import Any
from typing import Callable

class Consumer(ABC):
    def __init__(self):
        self.handlers = dict[str, list[Callable]]()

    def subscribe(self, topic: str, handler: Callable):
        self.handlers.setdefault(topic, []).append(handler)

    def consume(self, topic: str, message: Any):
        for handler in self.handlers.get(topic, []):
            handler(message)

    @abstractmethod
    def begin(self): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...

    @abstractmethod
    def close(self): ...


class Publisher:
    def __init__(self):
        self.consumers = list[Consumer]()

    def subscribe(self, consumer: Consumer):
        self.consumers.append(consumer)

    def publish(self, topic: str, message: Any):
        [consumer.consume(topic, message) for consumer in self.consumers]

    def begin(self):
        [consumer.begin() for consumer in self.consumers]

    def commit(self):
        [consumer.commit() for consumer in self.consumers]

    def rollback(self):
        [consumer.rollback() for consumer in self.consumers]

    def close(self):
        [consumer.close() for consumer in self.consumers]