
from domain.batch import Batch
from domain.order_line import OrderLine
import adapters.repository_batch as rb

from tests.common_test import get_session, clear_all

## SQLAlchemy

def test_repository_can_save_a_batch(session):
    batch = Batch("batch1", "SOAPDISH", 100, eta=None)

    repo = rb.SqlAlchemyBatchRepository(session)
    repo.add(batch)
    session.commit()
    query = """
        SELECT reference, sku, _purchased_quantity, eta from batches
    """
    rows = list(session.execute(query))
    assert rows == [("batch1", "SOAPDISH", 100, None)]


def test_repository_batch_list(session):
    batch1 = Batch("batch1", "SOAPDISH", 100, eta=None)
    batch2 = Batch("batch2", "FURNITURE", 50, eta=None)

    repo = rb.SqlAlchemyBatchRepository(session)
    repo.add(batch1)
    repo.add(batch2)
    session.commit()
    retrieved = repo.list()

    assert retrieved == [batch1,batch2]



def insert_order_line(session):
    query = """
        INSERT INTO order_lines(ref, sku, qty)
        VALUES 
        ('order1', 'SOFA', 12)
    """
    session.execute(query)
    query = """
        SELECT id fROM order_lines
        WHERE ref='{ref}' AND sku='{sku}'
    """.format(ref = "order1", sku="SOFA")
    [[orderline_id]] = session.execute(query)
    return orderline_id

def insert_batch(session, reference):
    query = """
        INSERT INTO batches (reference, sku, _purchased_quantity, eta)
        VALUES 
        ('{reference}', 'SOFA', 100, null)
    """.format(reference=reference)
    session.execute(query)
    query = """
        SELECT id fROM batches
        WHERE reference='{reference}' AND sku='{sku}'
    """.format(reference = reference, sku="SOFA")
    [[batch_id]] = session.execute(query)
    return batch_id

def insert_allocation(session, orderline_id, batch_id):
    query = """
        INSERT INTO allocations(orderline_id, batch_id)
        VALUES
        ({orderline_id},{batch_id})
    """.format(orderline_id=orderline_id, batch_id=batch_id)
    session.execute(query)

def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session,"batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = rb.SqlAlchemyBatchRepository(session)
    retrieved = repo.get_by_ref("batch1")

    expected = Batch("batch1", "SOFA", 100, eta=None)
    assert retrieved.reference == expected.reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "SOFA", 12)
    }


def test_repository_can_retrieve_a_batch_by_id(session):
    batch_id = insert_batch(session,"batch1")    
    repo = rb.SqlAlchemyBatchRepository(session)
    batch_ret = repo.get(batch_id)
    assert batch_ret.reference == "batch1"
    assert batch_ret.sku == "SOFA"


def test_repository_can_update_a_batch(session):
    batch_id = insert_batch(session,"batch1")    
    repo = rb.SqlAlchemyBatchRepository(session)
    batch_ret = repo.get(batch_id)
    batch_ret.reference = "changed"
    session.commit()
    batch_ret = repo.get(batch_id)
    assert batch_ret.reference == "changed"

def test_repository_can_delete_a_batch_by_id(session):
    batch_id = insert_batch(session,"batch1")    
    session.commit()
    repo = rb.SqlAlchemyBatchRepository(session)
    repo.delete(batch_id)
    session.commit()
    batches_ret = repo.list()
    assert len(batches_ret)==0
    

def test_repository_can_delete_a_batch_by_ref(session):
    batch_id = insert_batch(session,"batch1")    
    session.commit()
    repo = rb.SqlAlchemyBatchRepository(session)
    repo.delete_by_ref("batch1")
    session.commit()
    batches_ret = repo.list()
    assert len(batches_ret)==0


## Fake Repository

def test_fake_repository_add_and_retrieve_a_batch():
    batch = Batch("batch1", "SOAPDISH", 100, eta=None)

    repo = rb.FakeBatchRepository([])
    repo.add(batch)
    batch_ret = repo.get_by_ref("batch1")
    assert batch == batch_ret

def test_fake_repository_add_and_retrieve_a_batch_by_id():
    batch = Batch("batch1", "SOAPDISH", 100, eta=None)

    repo = rb.FakeBatchRepository([])
    repo.add(batch)
    batch_ret = repo.get(1)
    assert batch == batch_ret

def test_fake_repository_list_batches():
    batch1 = Batch("batch1", "SOAPDISH", 100, eta=None)
    batch2 = Batch("batch2", "SOAPDISH", 140, eta=None)
    repo = rb.FakeBatchRepository([batch1,batch2])
    batches_ret = repo.list()
    assert batch1 == batches_ret[0]
    assert batch2 == batches_ret[1]

def test_fake_repository_delete_batch():
    batch1 = Batch("batch1", "SOAPDISH", 100, eta=None)
    batch2 = Batch("batch2", "SOAPDISH", 140, eta=None)
    repo = rb.FakeBatchRepository([batch1,batch2])
    repo.delete(1)
    batches_ret = repo.list()
    assert len(batches_ret) == 1
    assert batches_ret[0] == batch2

def test_fake_repository_delete_batch_by_ref():
    batch1 = Batch("batch1", "SOAPDISH", 100, eta=None)
    batch2 = Batch("batch2", "SOAPDISH", 140, eta=None)
    repo = rb.FakeBatchRepository([batch1,batch2])
    repo.delete_by_ref("batch1")
    batches_ret = repo.list()
    assert len(batches_ret) == 1
    assert batches_ret[0] == batch2
