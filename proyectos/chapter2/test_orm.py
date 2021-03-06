import pytest

import model
from datetime import date
from common_test import get_session, clear_all



### END INIT STUFF


def test_orderline_mapper_can_load_lines():
    session = get_session()
    query = """
        INSERT INTO order_lines (ref, sku, qty) VALUES
        ('order1', 'CHAIR', 12),
        ('order2', 'TABLE', 13),
        ('order3', 'LIPSTICK', 14)
    """
    session.execute(query)
    expected = [
        model.OrderLine("order1", "CHAIR", 12),
        model.OrderLine("order2", "TABLE", 13),
        model.OrderLine("order3", "LIPSTICK", 14),
    ]
    obtained = session.query(model.OrderLine).all()
    clear_all()
    assert  obtained == expected

def test_orderline_mapper_can_save_lines():
    session = get_session()
    new_line = model.OrderLine("order1", "DECORATION", 12)
    session.add(new_line)
    session.commit()
    rows = list(session.execute("SELECT ref,sku,qty from 'order_lines'"))
    clear_all()
    assert rows == [("order1", "DECORATION",12)]

def test_retrieving_batches():
    session = get_session()    
    query = """
        INSERT INTO batches(reference, sku, _purchased_quantity, eta)
        VALUES 
        ('batch1', "sku1", 100, null),
        ('batch2', "sku2", 200, '2011-04-11');
    """
    session.execute(query)
    expected = [
        model.Batch("batch1", "sku1", 100, eta=None),
        model.Batch("batch2", "sku2", 200, eta=date(2011,4,11)),
    ]
    obtained = session.query(model.Batch).all()
    clear_all()
    assert obtained == expected


def test_saving_batches():
    session = get_session()        
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    session.add(batch)
    session.commit()
    rows = list(session.execute(
        "SELECT reference, sku, _purchased_quantity, eta from 'batches'"
    ))
    clear_all()
    assert rows == [('batch1', 'sku1', 100, None)]

def test_saving_allocations():
    session = get_session()        
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    line = model.OrderLine("order1", "sku1", 10)
    batch.allocate(line)
    session.add(batch)
    session.commit()
    query = """
        SELECT ol.ref, b.reference 
        FROM allocations a
        INNER JOIN order_lines ol on ol.id = a.id
        INNER JOIN batches b on b.id = a.id
    """
    rows = list(session.execute(query))
    assert rows == [(line.ref, batch.reference)]
    clear_all() # Si esto se coloca antes, se pierdes los atributos de los objetos.


def test_retrieveing_allocations():
    session = get_session()
    query = """
        INSERT INTO order_lines(ref, sku, qty)
        VALUES
        ('order1', 'sku1', 12);
    """
    session.execute(query)
    [[olid]] = session.execute(
        'SELECT id FROM order_lines WHERE ref=:ref AND sku=:sku',
        dict(ref='order1', sku='sku1')
    )
    query = """
        INSERT INTO batches(reference, sku, _purchased_quantity, eta)
        VALUES
        ('batch1', 'sku1', 100, null);
    """
    session.execute(query)
    [[bid]] = session.execute(
        'SELECT id FROM batches WHERE reference=:ref AND sku=:sku',
        dict(ref='batch1', sku='sku1')
    )
    query = """
        INSERT INTO allocations(orderline_id, batch_id)
        VALUES
        ({olid}, {bid})
    """.format(olid=olid, bid=bid)
    session.execute(query)
    batch = session.query(model.Batch).one()
    assert batch._allocations == {
        model.OrderLine("order1", "sku1", 12)
    }
    clear_all()
