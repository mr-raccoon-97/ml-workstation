from logging import getLogger
from workstation.protocols import Tensor
from workstation.callback import Handler
from workstation.core.schemas import Metric
from workstation.publisher import Publisher
from workstation.defaults.consumer import Consumer as Default
from logging import getLogger

logger = getLogger(__name__)

def on_call(metric: str, batch: int, value: float, phase: str, epoch: int):
    if batch % 100 == 0:
        logger.info(f'*** Metric {metric} on phase {phase} at epoch {epoch}')
        logger.info(f'--- Batch: {batch} ::: Value: {value}')

class _Average:
    def __init__(self):
        self.value = 0.0

    def update(self, sample: int, value: float) -> float:
        self.value = (self.value * (sample - 1) + value) / sample
        return self.value

    def reset(self):
        self.value = 0.0


class Loss(Handler):
    def __init__(self, publisher: Publisher | None = None):
        super().__init__(publisher or Publisher([Default()]))
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