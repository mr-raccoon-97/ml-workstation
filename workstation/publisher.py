from abc import ABC, abstractmethod
from typing import Any
from typing import Callable

class Consumer(ABC):
    def __init__(self):
        self.handlers = dict[type, list[Callable]]()

    def subscribe(self, message_type: type, handler: Callable):
        self.handlers.setdefault(message_type, []).append(handler)

    def consume(self, message: Any):
        for handler in self.handlers.get(type(message), []):
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
    def __init__(self, consumers: list[Consumer] = None):
        self.consumers = consumers or []

    def subscribe(self, consumer: Consumer):
        self.consumers.append(consumer)

    def publish(self, message: Any):
        [consumer.consume(message) for consumer in self.consumers]

    def begin(self):
        [consumer.begin() for consumer in self.consumers]

    def commit(self):
        [consumer.commit() for consumer in self.consumers]

    def rollback(self):
        [consumer.rollback() for consumer in self.consumers]

    def close(self):
        [consumer.close() for consumer in self.consumers]