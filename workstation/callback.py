from abc import ABC, abstractmethod
from typing import Any
from workstation.publisher import Publisher
from workstation.defaults.consumer import Consumer as Default

class Handler(ABC):
    def __init__(self):
        self.publisher = Publisher([Default()])
        self.epoch = 0
        self.phase = None        

    @abstractmethod
    def __call__(self, *args, **kargs): ...

    @abstractmethod
    def flush(self): ...

    @abstractmethod
    def reset(self): ...
    

class Callback:
    def __init__(self, handlers: list[Handler] = None):
        self.handlers = handlers or []
        self.epoch = 0
        self.phase = None
        self.publisher = Publisher([Default()])

    def bind(self, publisher: Publisher):
        self.publisher = publisher
        [setattr(handler, 'publisher', self.publisher) for handler in self.handlers]

    def setup(self, name: str):
        self.publisher.setup(name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name in ('epoch', 'phase'):
            [setattr(handler, name, value) for handler in self.handlers]
        return super().__setattr__(name, value)

    def __call__(self, *args, **kargs):
        [handler(*args, **kargs) for handler in self.handlers]        

    def flush(self):
        [handler.flush() for handler in self.handlers]

    def reset(self):
        self.epoch = 0
        [handler.reset() for handler in self.handlers]
    

    def begin(self):
        self.publisher.begin()

    def commit(self):
        self.publisher.commit()

    def rollback(self):
        self.reset()
        self.publisher.rollback()

    def close(self):
        self.publisher.close()

    def deliver(self, message: Any):
        self.publisher.publish(message)