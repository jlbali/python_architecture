
from domain.order_line import OrderLine
import adapters.repository_order_line as rol

from tests.common_test import get_session, clear_all

## SQLAlchemy

def test_repository_can_save_an_order_line():
    session = get_session()
    item = OrderLine("order1", "SOAPDISH", 50)

    repo = rol.SqlAlchemyOrderLineRepository(session)
    repo.add(item)
    session.commit()
    query = """
        SELECT ref, sku, qty from order_lines
    """
    rows = list(session.execute(query))
    assert rows == [("order1", "SOAPDISH", 50)]
    clear_all()


def test_repository_order_line_list():
    session = get_session()
    item1 = OrderLine("order1", "SOAPDISH", 50)
    item2 = OrderLine("order2", "SOAPDISH", 70)

    repo = rol.SqlAlchemyOrderLineRepository(session)
    repo.add(item1)
    repo.add(item2)
    session.commit()
    retrieved = repo.list()
    assert retrieved == [item1,item2]
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

def test_repository_can_retrieve_an_order_line_by_id():
    session = get_session()
    item_id = insert_order_line(session)    
    session.commit()
    repo = rol.SqlAlchemyOrderLineRepository(session)
    item_ret = repo.get(item_id)
    assert item_ret.ref == "order1"
    assert item_ret.sku == "SOFA"
    clear_all()


def test_repository_can_update_an_order_line():
    session = get_session()
    item_id = insert_order_line(session)    
    repo = rol.SqlAlchemyOrderLineRepository(session)
    item_ret = repo.get(item_id)
    item_ret.reference = "changed"
    session.commit()
    item_ret = repo.get(item_id)
    assert item_ret.reference == "changed"
    clear_all()

def test_repository_can_delete_an_order_line_by_id():
    session = get_session()
    item_id = insert_order_line(session)    
    session.commit()
    repo = rol.SqlAlchemyOrderLineRepository(session)
    repo.delete(item_id)
    session.commit()
    items_ret = repo.list()
    assert len(items_ret)==0
    clear_all()
    

def test_repository_can_delete_an_order_line_by_ref():
    session = get_session()
    item_id = insert_order_line(session)    
    session.commit()
    repo = rol.SqlAlchemyOrderLineRepository(session)
    repo.delete_by_ref("order1")
    session.commit()
    items_ret = repo.list()
    assert len(items_ret)==0
    clear_all()


## Fake Repository

def test_fake_repository_add_and_retrieve_an_order_line():
    item = OrderLine("order1", "SOAP", 45)
    repo = rol.FakeOrderLineRepository([])
    repo.add(item)
    item_ret = repo.get_by_ref("order1")
    assert item == item_ret

def test_fake_repository_add_and_retrieve_a_batch_by_id():
    item = OrderLine("order1", "SOAP", 45)
    repo = rol.FakeOrderLineRepository([])
    repo.add(item)
    item_ret = repo.get(1)
    assert item == item_ret

def test_fake_repository_list_order_lines():
    item1 = OrderLine("order1", "SOAP", 45)    
    item2 = OrderLine("order2", "SOAP", 60)    
    repo = rol.FakeOrderLineRepository([item1,item2])
    items_ret = repo.list()
    assert item1 == items_ret[0]
    assert item2 == items_ret[1]

def test_fake_repository_delete_order_line():
    item1 = OrderLine("order1", "SOAP", 45)    
    item2 = OrderLine("order2", "SOAP", 60)    
    repo = rol.FakeOrderLineRepository([item1,item2])
    repo.delete(1)
    items_ret = repo.list()
    assert len(items_ret) == 1
    assert items_ret[0] == item2

def test_fake_repository_delete_batch_by_ref():
    item1 = OrderLine("order1", "SOAP", 45)    
    item2 = OrderLine("order2", "SOAP", 60)    
    repo = rol.FakeOrderLineRepository([item1,item2])
    repo.delete_by_ref("order1")
    items_ret = repo.list()
    assert len(items_ret) == 1
    assert items_ret[0] == item2
