from torch.nn import CrossEntropyLoss
from torch.optim import Adam
from examples.models.perceptrons import MLP, GLU
from examples.datasets.mnist import Digits
from workstation.session import Session
from workstation.publisher import Publisher
from workstation.pytorch import Repository, Loaders, Compiler
from workstation.pytorch.callbacks import Callback, Accuracy, Loss
from workstation.remote.consumer import RabbitMQ
from workstation.defaults.consumer import Consumer as DefaultConsumer

from logging import basicConfig, INFO

basicConfig(level=INFO)

Repository.models.register(MLP)
Repository.models.register(GLU)
Repository.optimizers.register(Adam)
Repository.criterions.register(CrossEntropyLoss)
Repository.datasets.register(Digits)

repository = Repository(experiment_name='glu-perceptrons')

for hidden_dimension in [256, 512, 1024]:
    for activation in ['relu', 'gelu', 'silu']:
        for p in [0.0, 0.2, 0.3, 0.4, 0.5]:

                model = GLU(input_dimension=784, hidden_dimension=hidden_dimension, output_dimension=10, p=p, activation=activation)
                criterion = CrossEntropyLoss()
                optimizer = Adam(model.parameters(), lr=0.01)

                compiler = Compiler()
                classifier = compiler.compile(model, criterion, optimizer)

                loaders = Loaders()
                loaders.add('train', Digits(train=True, normalize=True), batch_size=1024, shuffle=True)
                loaders.add('test', Digits(train=False, normalize=True), batch_size=1024, shuffle=False)

                with RabbitMQ() as broker:
                    rabbitmq_consumer = broker.consumer
                    rabbitmq_consumer.setup(experiment_name='glu-perceptrons')
                    default_consumer = DefaultConsumer()

                    publisher = Publisher([rabbitmq_consumer, default_consumer])
                    callback = Callback([Loss(), Accuracy()])
                    callback.bind(publisher)

                    with Session(classifier, loaders, repository, callback):
                        while classifier.epoch < 5:
                            classifier.epoch += 1
                            for phase, loader in loaders:
                                classifier.phase = phase
                                classifier.iterate(loader, callback)