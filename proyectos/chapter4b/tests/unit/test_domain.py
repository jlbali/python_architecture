from datetime import date, timedelta
import pytest

from domain.batch import Batch, allocate
from domain.order_line import OrderLine
from domain.exceptions import OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def make_batch_and_line(sku:str, batch_qty:int, line_qty:int) -> (Batch, OrderLine):
    batch = Batch("batch-001", sku, batch_qty, eta=date.today())
    line = OrderLine("order-123", sku, line_qty)
    return batch,line

def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_batch_and_line("SMALL-TABLE", 20, 2)
    batch.allocate(line)
    assert batch.available_quantity == 18

def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)

def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("SMALL-TABLE", 2, 2)
    assert batch.can_allocate(line)

def test_cannot_allocate_if_skus_no_not_match():
    batch = Batch("batch-001", "CHAIR", 100, eta=None)
    line = OrderLine("order-123", "TOASTER", 10)
    assert batch.can_allocate(line) is False

def test_can_only_deallocate_allocated_lines():
    batch, line = make_batch_and_line("TRINKET", 20,2)
    batch.deallocate(line)
    assert batch.available_quantity == 20

def test_deallocation_test():
    batch, line = make_batch_and_line("TRINKET", 20,2)
    batch.allocate(line)
    assert batch.available_quantity == 18
    batch.deallocate(line)
    assert batch.available_quantity == 20

def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "CLOCK", 100, eta=tomorrow)
    line =OrderLine("oref", "CLOCK",10)
    allocate(line, [in_stock_batch, shipment_batch])
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100

def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "SPOON", 100, eta=today)
    medium = Batch("normal-batch", "SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "SPOON", 100, eta=later)
    line = OrderLine("order1", "SPOON", 10)
    allocate(line, [medium, earliest, latest])
    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100

def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch", "SPOON", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "SPOON", 100, eta=tomorrow)
    line = OrderLine("order1", "SPOON", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference

def test_raises_out_of_stock_exception_it_cannot_allocate():
    batch = Batch("batch1", "FORK", 10, eta=today)
    allocate(OrderLine("order1", "FORK", 10), [batch])
    with pytest.raises(OutOfStock, match="FORK"):
        allocate(OrderLine("order2", "FORK", 1), [batch])

