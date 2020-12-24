from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Set, NewType

@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref:str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: Set[OrderLine] = set()

    @property
    def allocalted_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocalted_quantity


    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            if self.can_allocate(line):
                self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine):
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other: Batch):
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)
