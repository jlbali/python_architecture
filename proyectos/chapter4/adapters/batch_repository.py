import abc
from domain.batch import Batch
from typing import List

class AbstractBatchRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference:str) -> Batch:
        raise NotImplementedError


class SqlAlchemyBatchRepository(AbstractBatchRepository):

    def __init__(self, session):
        self.session = session
    
    def add(self, batch: Batch):
        self.session.add(batch)
    
    def get(self, reference:str) -> Batch:
        return self.session.query(Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(Batch).all()


def FakeBatchRepository(AbstractBatchRepository):

    def __init__(self, batches: List[Batch]=[]):
        self._batches = set(batches)
    
    def add(self, batch: Batch):
        self._batches.add(batch)
    
    def get(self, reference:str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[Batch]:
        return list(self._batches)

