import abc
from domain.order_line import OrderLine
from typing import List, Optional

class AbstractOrderLineRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, item: OrderLine):
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_ref(self, reference:str) -> OrderLine:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, id:int) -> OrderLine:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[OrderLine]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, id:int):
        raise NotImplementedError

    @abc.abstractmethod
    def delete_by_ref(self, reference:str):
        raise NotImplementedError



class SqlAlchemyOrderLineRepository(AbstractOrderLineRepository):

    def __init__(self, session):
        self.session = session
    
    def add(self, item: OrderLine):
        self.session.add(item)
    
    def get_by_ref(self, reference:str) -> OrderLine:
        return self.session.query(OrderLine).filter_by(ref=reference).one()

    def get(self, id:int) -> OrderLine:
        return self.session.query(OrderLine).get(id)

    def list(self) -> List[OrderLine]:
        return self.session.query(OrderLine).all()

    def delete(self, id:int):
        self.session.query(OrderLine).filter(OrderLine.id==id).delete()

    def delete_by_ref(self, reference:str):
        self.session.query(OrderLine).filter(OrderLine.ref==reference).delete()



class FakeOrderLineRepository(AbstractOrderLineRepository):

    def __init__(self, items: List[OrderLine]=[]):
        self._current_id = 1
        self._items = []
        for item in items:
            self.add(item)
        
    
    def add(self, item: OrderLine):
        item.id = self._current_id
        self._items.append(item)
        self._current_id += 1
    
    def get(self, id: int) -> OrderLine:
        return next(item for item in self._items if item.id == id)

    def get_by_ref(self, reference: str) -> OrderLine:
        return next(item for item in self._items if item.ref == reference)

    def list(self) -> List[OrderLine]:
        return self._items

    def delete(self, id:int):
        self._items = [item for item in self._items if not item.id == id]

    def delete_by_ref(self, reference:str):
        self._items = [item for item in self._items if not item.ref == reference]
