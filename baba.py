from uuid import uuid3, UUID, NAMESPACE_DNS
from inspect import getfullargspec
from typing import Any
from json import dumps
from workstation.protocols import Loader
from logging import getLogger
from hashlib import md5

logger = getLogger(__name__)

def type_parameters(type: type, excluded_parameters: set[str]) -> dict[str, str]:
    init = type.__init__
    argspec = getfullargspec(init)
    annotations = { key: (value.__name__ if value is not None else Any.__name__)  for key, value in argspec.annotations.items() }    
    parameters = { key: annotations.get(key, Any.__name__)  for key in argspec.args if key not in excluded_parameters }    
    return parameters

def type_identifier(type: type, excluded_parameters: set[str]) -> dict[str, str]:
    name = type.__name__
    name += dumps(type_parameters(type, excluded_parameters), sort_keys=True)
    return uuid3(NAMESPACE_DNS, name)

def object_hashing(object: object, args, kwargs, excluded_parameters: set[str]) -> UUID:
    name = object.__class__.__name__
    name += dumps(type_parameters(object, excluded_parameters), sort_keys=True)
    for arg in args:
        name += str(arg)
    name += dumps(kwargs, sort_keys=True)
    return md5(name.encode()).hexdigest()

class Registry[T: type]:
    def __init__(self, aditional_parameters: dict[str, Any] = None, exclude_parameters: set[str] = None, excluded_positions: list[int] = None):
        self.types = dict()
        self.states = dict()
        self.excluded_postitions = excluded_positions or []
        self.aditional_parameters = aditional_parameters or dict()
        self.excluded_parameters = ( exclude_parameters or set[str]() ) | {'self', 'return'}

    def register(self, type: T) -> T:
        identifier, parameters = type_identifier(type, self.excluded_parameters), type_parameters(type, self.excluded_parameters)
        self.types[type.__name__] = (type, parameters)
        init = type.__init__

        def wrapper(obj, *args, **kwargs):
            included_args = { arg for index, arg in enumerate(args) if index not in self.excluded_postitions }
            included_kwargs = { key: value for key, value in kwargs.items() if key not in self.excluded_parameters } | self.aditional_parameters
            self.states[identifier] = (included_args, included_kwargs)
            init(obj, *args, **kwargs)
            setattr(obj, 'metadata', {
                'hash': object_hashing(obj, included_args, included_kwargs, self.excluded_parameters),
                'name': type.__name__,
                'args': included_args,
                'kwargs': included_kwargs,
            })
        type.__init__ = wrapper
        return type    

def register_loader(phase: str, loader: Loader):
    try:
        loader.metadata['phase'] = phase
        loader.metadata['dataset'] = loader.dataset.metadata
    except Exception as error:
        logger.warning(f'loader {loader} could not be registered: {error}')



models = Registry(aditional_parameters={'epochs': 0})

class Model:
    def __init__(self, input_size: int, output_size: int, hidden_size: int):
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.epochs = 0

models.register(Model)

model = Model(10, 10, 10)
print(model.metadata)

model.epochs = 10
print(model.metadata)
