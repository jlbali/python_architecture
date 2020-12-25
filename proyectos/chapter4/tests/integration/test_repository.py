
from domain.batch import Batch
from domain.order_line import OrderLine
import adapters.batch_repository as br

from tests.common_test import get_session, clear_all

def test_repository_can_save_a_batch():
    session = get_session()
    batch = Batch("batch1", "SOAPDISH", 100, eta=None)

    repo = br.SqlAlchemyBatchRepository(session)
    repo.add(batch)
    session.commit()
    query = """
        SELECT reference, sku, _purchased_quantity, eta from batches
    """
    rows = list(session.execute(query))
    assert rows == [("batch1", "SOAPDISH", 100, None)]
    clear_all()

def test_repo_list_function():
    session = get_session()
    batch1 = Batch("batch1", "SOAPDISH", 100, eta=None)
    batch2 = Batch("batch2", "FURNITURE", 50, eta=None)

    repo = br.SqlAlchemyBatchRepository(session)
    repo.add(batch1)
    repo.add(batch2)
    session.commit()
    retrieved = repo.list()

    assert retrieved == [batch1,batch2]
    clear_all()



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

def test_repository_can_retrieve_a_batch_with_allocations():
    session = get_session()
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session,"batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = br.SqlAlchemyBatchRepository(session)
    retrieved = repo.get("batch1")

    expected = Batch("batch1", "SOFA", 100, eta=None)
    assert retrieved.reference == expected.reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "SOFA", 12)
    }
    clear_all()

