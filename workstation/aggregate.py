from typing import Any
from typing import overload
from typing import Protocol, Callable, Iterator
from typing import Optional
from abc import ABC, abstractmethod
from workstation.protocols import Callback, Module, Criterion, Optimizer, Tensor, Loader

class Registry[T](ABC):

    @abstractmethod
    def register(self, type: type[T]) -> type[T]: ...

class Aggregate(Protocol):
    id: Any
    epoch: int
    phase: str
    model: Module
    callback: Callback
    criterion: Optional[Criterion]
    optimizer: Optional[Optimizer]

    def fit(self, *args, **kwargs) -> Any: ...

    def evaluate(self, *args, **kwargs) -> Any: ...

    def iterate(self, *args, **kwargs) -> Any: ...

    @overload
    def fit(self, input: Tensor, target: Tensor) -> tuple[Tensor, float]: ...

    @overload
    def evaluate(self, input: Tensor, target: Tensor) -> tuple[Tensor, float]: ...

    @overload
    def iterate(self, loader: Loader) -> None: ...


class Loaders(ABC):
    registry: Registry[Loader]
    
    def __init__(self, registry: Registry[Loader]):
        self.list = list[tuple[str, Loader]]()
        self.registry = registry

    @abstractmethod
    def add(self, phase: str, loader: Loader, *args, **kwargs) -> None: ...

    def __iter__(self) -> Iterator[tuple[str, Loader]]:
        return iter(self.list)

    
class Compiler(Protocol):

    def compile(self, *args, **kwargs) -> Aggregate: ...