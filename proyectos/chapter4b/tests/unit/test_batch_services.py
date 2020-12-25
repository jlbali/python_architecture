import pytest
from domain.batch import Batch
from domain.order_line import OrderLine
from adapters.repository_batch import FakeBatchRepository
from service_layer.batch_services import InvalidSku, allocate, add_batch, get_batch, get_batches

class FakeSession():
    committed = False

    def commit(self):
        self.committed = True

def test_returns_allocation():
    line = OrderLine("o1", "LAMP", 10)
    batch = Batch("b1", "LAMP", 100, eta=None)
    repo = FakeBatchRepository([batch])
    result = allocate(line, repo, FakeSession())
    assert result == "b1"
    assert batch.allocated_quantity == 10
    assert batch.available_quantity == 90

def test_error_for_invalid_sku():
    line = OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeBatchRepository([batch])
    with pytest.raises(InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        allocate(line, repo, FakeSession())

def test_commit():
    line = OrderLine("o1", "MIRROR", 10)
    batch = Batch("b1", "MIRROR", 100, eta=None)
    repo = FakeBatchRepository([batch])
    session = FakeSession()
    allocate(line, repo, session)
    assert session.committed is True


def test_add_get_batch():
    session = FakeSession()
    repo = FakeBatchRepository([])
    id = add_batch("b1", "LAMP", 250, None, repo, session)
    batch = get_batch(id, repo)
    assert batch.reference == "b1"
    assert batch.sku == "LAMP"
    assert batch.available_quantity == 250


def test_add_get_batches():
    session = FakeSession()
    repo = FakeBatchRepository([])
    add_batch("b1", "LAMP", 250, None, repo, session)
    add_batch("b2", "LAMP", 20, None, repo, session)
    batches = get_batches(repo)
    assert len(batches) == 2

