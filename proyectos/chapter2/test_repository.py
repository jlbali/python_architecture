
import model
import repository

from common_test import get_session, clear_all

def test_repository_can_save_a_batch():
    session = get_session()
    batch = model.Batch("batch1", "SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyBatchRepository(session)
    repo.add(batch)
    session.commit()
    query = """
        SELECT reference, sku, _purchased_quantity, eta from batches
    """
    rows = list(session.execute(query))
    assert rows == [("batch1", "SOAPDISH", 100, None)]
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

    repo = repository.SqlAlchemyBatchRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "SOFA", 100, eta=None)
    assert retrieved.reference == expected.reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "SOFA", 12)
    }


