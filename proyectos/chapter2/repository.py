import abc
import model


class AbstractBatchRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference:str):
        raise NotImplementedError

