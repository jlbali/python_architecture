from domain.batch import Batch, allocate as alloc_domain
from domain.order_line import OrderLine
from typing import List, Optional
from adapters.repository_batch import AbstractBatchRepository
from datetime import date


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: List[Batch]) -> bool:
    return sku in {b.sku for b in batches}

def allocate(line: OrderLine, repo: AbstractBatchRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batchref = alloc_domain(line, batches)
    session.commit()
    return batchref

def add_batch(
        ref: str, sku: str, qty: int, eta: Optional[date],
        repo: AbstractBatchRepository, session,
):
    repo.add(Batch(ref, sku, qty, eta))
    session.commit()


