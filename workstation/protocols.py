from typing import Protocol
from typing import Any
from typing import Iterator
from typing import overload
from typing import Tuple

class Tensor(Protocol):
    def to(self, device: str) -> 'Tensor': ...


class Module(Protocol):
    ...

class Criterion(Protocol):
    ...


class Optimizer(Protocol):
    ...


class Dataset(Protocol):
    ...

class Loader(Protocol):
    dataset: Dataset
    
    def __iter__(self) -> Iterator[Any]: ...

    @overload
    def __iter__(self) -> Iterator[Tuple[Tensor, Tensor]]: ...


class Handler(Protocol):

    def __call__(self, *args, **kargs): ...

    def flush(self): ...

    def reset(self): ...
    

class Callback(Protocol):
    handlers: list[Handler]
    
    def __setattr__(self, name: str, value: Any) -> None: ... 

    def __call__(self, *args, **kargs): ...

    def flush(self): ...

    def reset(self): ...

    def begin(self): ...

    def commit(self): ...

    def rollback(self): ...

    def close(self): ...