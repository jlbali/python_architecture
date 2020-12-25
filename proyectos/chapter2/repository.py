import abc
import model
from typing import List

class AbstractBatchRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference:str) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyBatchRepository(AbstractBatchRepository):

    def __init__(self, session):
        self.session = session
    
    def add(self, batch: model.Batch):
        self.session.add(batch)
    
    def get(self, reference:str) -> model.Batch:
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


def FakeBatchRepository(AbstractBatchRepository):

    def __init__(self, batches: List[model.Batch]=[]):
        self._batches = set(batches)
    
    def add(self, batch: model.Batch):
        self._batches.add(batch)
    
    def get(self, reference:str) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[model.Batch]:
        return list(self._batches)

