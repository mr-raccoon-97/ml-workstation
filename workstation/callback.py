from abc import ABC, abstractmethod
from typing import Any
from workstation.publisher import Publisher

class Handler(ABC):
    def __init__(self, publisher: Publisher):
        self.publisher = publisher
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
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name in ('epoch', 'phase'):
            [setattr(handler, name, value) for handler in self.handlers]
        return super().__setattr__(name, value)

    def __call__(self, *args, **kargs):
        [handler(*args, **kargs) for handler in self.handlers]        

    def flush(self):
        [handler.flush() for handler in self.handlers]

    def reset(self):
        [handler.reset() for handler in self.handlers]

    def begin(self):
        [handler.publisher.begin() for handler in self.handlers]

    def commit(self):
        [handler.publisher.commit() for handler in self.handlers]

    def rollback(self):
        [handler.publisher.rollback() for handler in self.handlers]

    def close(self):
        [handler.publisher.close() for handler in self.handlers]