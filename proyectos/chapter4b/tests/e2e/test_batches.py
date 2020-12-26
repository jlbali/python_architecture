import uuid
import pytest
import requests

import config
from domain.batch import Batch
from dateutil.parser import parse
from dateutil.tz import tzutc
from datetime import datetime
from typing import List

def random_suffix():
    return uuid.uuid4().hex[:6]

def random_sku(name=''):
    return f'sku-{name}-{random_suffix()}'

def random_batchref(name=''):
    return f'batch-{name}-{random_suffix()}'

def random_orderid(name=''):
    return f'order-{name}-{random_suffix()}'


def post_to_add_batch(ref, sku, qty, eta):
    url = config.get_api_url()
    r = requests.post(
        f'{url}/batch',
        json={'ref': ref, 'sku': sku, 'qty': qty, 'eta': eta}
    )
    assert r.status_code == 201
    return int(r.json()["id"])

def get_api_batch(id: int) -> Batch:
    url = config.get_api_url()
    r = requests.get(
        f'{url}/batch/' + str(id)
    )
    assert r.status_code == 200
    obj_json = r.json()

    batch = Batch(obj_json["reference"], obj_json["sku"], int(obj_json["_purchased_quantity"]),
        #datetime.fromisoformat(obj_json["eta"]).date()
       parse(obj_json["eta"]),
    )
    batch.id = id
    return batch

def get_api_batches() -> List[Batch]:
    url = config.get_api_url()
    r = requests.get(
        f'{url}/batches'
    )
    assert r.status_code == 200
    objs_json = r.json()
    #print(objs_json)
    batches = []
    for obj_json in objs_json:
        eta = parse(obj_json["eta"]) if not obj_json["eta"] is None else None
        batch = Batch(obj_json["reference"], obj_json["sku"], int(obj_json["_purchased_quantity"]), eta) 
        batch.id = obj_json["id"]
        batches.append(batch)
    return batches


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_happy_path_returns_201_and_allocated_batch():
    sku, othersku = random_sku(), random_sku('other')
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    post_to_add_batch(laterbatch, sku, 100, '2011-01-02')
    post_to_add_batch(earlybatch, sku, 100, '2011-01-01')
    post_to_add_batch(otherbatch, othersku, 100, None)
    data = {'orderid': random_orderid(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 201
    assert r.json()['batchref'] == earlybatch


@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {'orderid': orderid, 'sku': unknown_sku, 'qty': 20}
    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()['message'] == f'Invalid sku {unknown_sku}'

@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_add_and_get_batch():
    sku = random_sku()
    reference = random_batchref(1)
    id = post_to_add_batch(reference, sku, 100, '2011-01-02')
    ret_batch = get_api_batch(id)
    assert ret_batch.id == id
    assert ret_batch.reference == reference
    assert ret_batch.sku == sku
    assert ret_batch._purchased_quantity == 100
    assert ret_batch.eta == datetime(2011,1,2, tzinfo=tzutc())

@pytest.mark.usefixtures('postgres_db')
@pytest.mark.usefixtures('restart_api')
def test_get_batches():
    sku1 = random_sku()
    reference1 = random_batchref(1)
    id1 = post_to_add_batch(reference1, sku1, 100, '2011-01-02')
    sku2 = random_sku()
    reference2 = random_batchref(1)
    id2 = post_to_add_batch(reference2, sku2, 150, '2020-01-02')
    batches = get_api_batches()
    ids = [batch.id for batch in batches]
    assert id1 in ids
    assert id2 in ids
