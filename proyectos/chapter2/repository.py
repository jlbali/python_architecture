import abc
import model


class AbstractBatchRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference:str):
        raise NotImplementedError


class SqlAlchemyBatchRepository(AbstractBatchRepository):

    def __init__(self, session):
        self.session = session
    
    def add(self, batch: model.Batch):
        self.session.add(batch)
    
    def get(self, reference:str):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()
