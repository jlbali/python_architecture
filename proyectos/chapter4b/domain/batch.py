
from datetime import date
from typing import Optional, List, Set, NewType
from domain.order_line import OrderLine
from domain.exceptions import OutOfStock

# El id podría ser parte del modelo...


class Batch:
    def __init__(self, ref:str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity


    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
    
    def as_dict(self):
        #return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d = {
           "reference": self.reference,
           "sku": self.sku,
           "_purchased_quantity": self._purchased_quantity,
           "eta": self.eta,
        }
        if hasattr(self, 'id'):
            d["id"] = self.id
        return d
    


# Allocate an order to the first available batch that can handle.
def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')
    batch.allocate(line)
    return batch.reference

