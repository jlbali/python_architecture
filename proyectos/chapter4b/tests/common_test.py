from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from adapters.orm import metadata, start_mappers

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