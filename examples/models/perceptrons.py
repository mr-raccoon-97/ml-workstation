from torch import Tensor
from torch import chunk
from torch.nn import Module, Flatten
from torch.nn import Linear, ReLU, GELU, SiLU
from torch.nn import Dropout

def select(activation: str) -> Module:
    match activation:
        case 'relu':
            return ReLU()
        case 'gelu':
            return GELU()
        case 'silu':
            return SiLU()
        case _:
            raise ValueError(f'Activation {activation} not supported')      

class MLP(Module):
    def __init__(self, input_dimension: int, hidden_dimension: int, output_dimension: int, p: float, activation: str):
        super().__init__()
        self.activation = select(activation)
        self.dropout = Dropout(p)
        self.input_layer = Linear(input_dimension, hidden_dimension)
        self.output_layer = Linear(hidden_dimension, output_dimension)

    def forward(self, sequence: Tensor) -> Tensor:
        sequence = self.input_layer(sequence.flatten(1))
        sequence = self.activation(sequence)
        sequence = self.dropout(sequence)
        return self.output_layer(sequence)

class GLU(Module):
    def __init__(self, input_dimension: int, hidden_dimension: int, output_dimension: int, p: float, activation: str):
        super().__init__()
        self.activation = select(activation)
        self.hidden_dimension = int(hidden_dimension * 2 / 3)
        self.dropout = Dropout(p)
        self.input_layer = Linear(input_dimension, 2* self.hidden_dimension)
        self.output_layer = Linear(self.hidden_dimension, output_dimension)

    def forward(self, sequence: Tensor) -> Tensor:
        sequence = self.input_layer(sequence.flatten(1))
        sequence, gate = chunk(sequence, 2, dim=-1)
        sequence = self.activation(sequence)
        sequence = self.dropout(sequence)
        sequence = sequence * gate
        return self.output_layer(sequence)