from torch.nn import CrossEntropyLoss
from torch.optim import Adam
from examples.models.perceptrons import MLP
from examples.datasets.mnist import Digits
from workstation.pytorch import Repository, Loaders, Compiler
from workstation.pytorch.callbacks import Callback, Accuracy, Loss
from workstation.publisher import Publisher
from workstation.session import Session
from workstation.defaults.consumer import Consumer
from logging import basicConfig, INFO

basicConfig(level=INFO)

Repository.models.register(MLP)
Repository.optimizers.register(Adam)
Repository.criterions.register(CrossEntropyLoss)
Repository.datasets.register(Digits)

repository = Repository()
model = MLP(input_dimension=784, hidden_dimension=256, output_dimension=10, p=0.2, activation='relu')
criterion = CrossEntropyLoss()
optimizer = Adam(model.parameters(), lr=0.001)

compiler = Compiler()
classifier = compiler.compile(model, criterion, optimizer)

loaders = Loaders()
loaders.add('train', Digits(train=True), batch_size=32, shuffle=True)
loaders.add('test', Digits(train=False), batch_size=32, shuffle=False)

publisher = Publisher([Consumer()])
callback = Callback([Loss(), Accuracy()])
callback.bind(publisher)

classifier.epoch = 5

with Session(classifier, loaders, repository, callback):
    for epoch in range(5):
        classifier.epoch += 1
        for phase, loader in loaders:
            classifier.phase = phase
            classifier.iterate(loader, callback)

assert classifier.epoch == 10

with Session(classifier, loaders, repository, callback):
    for epoch in range(5):
        classifier.epoch += 1
        for phase, loader in loaders:
            classifier.phase = phase
            classifier.iterate(loader, callback)
        if epoch == 2:
            raise Exception('ERROR')

assert classifier.epoch == 10