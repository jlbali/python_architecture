import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import metadata, start_mappers
import model
from datetime import date


### COMMON STUFF ###########

def get_in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine

def get_session():
    start_mappers()
    return sessionmaker(bind=get_in_memory_db())()

def clear_all():
    clear_mappers()

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


