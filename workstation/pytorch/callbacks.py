from torch import Tensor
from torch import Tensor, argmax

from workstation.callback import Handler, Callback
from workstation.publisher import Publisher
from workstation.signals import Metric
from workstation.pytorch.logging import on_call

class _Average:
    def __init__(self):
        self.value = 0.0

    def update(self, sample: int, value: float) -> float:
        self.value = (self.value * (sample - 1) + value) / sample
        return self.value

    def reset(self):
        self.value = 0.0

        
def accuracy(predictions: Tensor, target: Tensor) -> float:
    return (predictions == target).float().mean().item()

def predictions(output: Tensor) -> Tensor:
    return argmax(output, dim=1)


class Loss(Handler):
    def __init__(self, publisher: Publisher = None):
        super().__init__(publisher)
        self.average = _Average()

    def __call__(self, batch: int, input: Tensor, output: Tensor, target: Tensor, loss: float):
        self.batch = batch
        value = self.average.update(batch, loss)        
        on_call('loss', batch, value, self.phase, self.epoch)

    def flush(self):
        self.publisher.publish(Metric('loss', self.phase, self.batch, self.epoch, self.average.value))
        self.average.reset()

    def reset(self):
        self.average.reset()
        

class Accuracy(Handler):
    def __init__(self, publisher: Publisher = None):
        super().__init__(publisher)
        self.average = _Average()

    def __call__(self, batch: int, input: Tensor, output: Tensor, target: Tensor, loss: float):
        self.batch = batch
        value = self.average.update(batch, accuracy(predictions(output), target))
        on_call('accuracy', batch, value, self.phase, self.epoch)

    def flush(self):
        self.publisher.publish(Metric('accuracy', self.phase, self.batch, self.epoch, self.average.value))
        self.average.reset()

    def reset(self):
        self.average.reset()