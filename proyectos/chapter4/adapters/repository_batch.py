import abc
from domain.batch import Batch
from typing import List, Optional

class AbstractBatchRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_ref(self, reference:str) -> Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id:int) -> Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[Batch]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id:int):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_ref(self, reference:str):
        raise NotImplementedError



class SqlAlchemyBatchRepository(AbstractBatchRepository):

    def __init__(self, session):
        self.session = session
    
    def add(self, batch: Batch):
        self.session.add(batch)
    
    def get_by_ref(self, reference:str) -> Batch:
        return self.session.query(Batch).filter_by(reference=reference).one()

    def get(self, id:int) -> Batch:
        return self.session.query(Batch).get(id)

    def list(self) -> List[Batch]:
        return self.session.query(Batch).all()

    def delete(self, id:int):
        self.session.query(Batch).filter(Batch.id==id).delete()

    def delete_by_ref(self, reference:str):
        self.session.query(Batch).filter(Batch.reference==reference).delete()



class FakeBatchRepository(AbstractBatchRepository):

    def __init__(self, batches: List[Batch]=[]):
        self._current_id = 1
        self._batches = []
        for batch in batches:
            self.add(batch)
        
    
    def add(self, batch: Batch):
        batch.id = self._current_id
        self._batches.append(batch)
        self._current_id += 1
    
    def get(self, id: int) -> Batch:
        return next(b for b in self._batches if b.id == id)

    def get_by_ref(self, reference: str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> List[Batch]:
        return self._batches

    def delete(self, id:int):
        self._batches = [batch for batch in self._batches if not batch.id == id]

    def delete_by_ref(self, reference:str):
        self._batches = [batch for batch in self._batches if not batch.reference == reference]
