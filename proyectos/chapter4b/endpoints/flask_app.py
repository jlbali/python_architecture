from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

import config
from domain.order_line import OrderLine
from domain.exceptions import OutOfStock
import adapters.orm as orm
import adapters.repository_batch as batch_repository
import service_layer.batch_services as batch_services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/ping", methods=['GET'])
def ping():
    return 'pong', 200


### BATCHES ##########

@app.route("/batch", methods=['POST'])
def add_batch():
    session = get_session()
    repo = batch_repository.SqlAlchemyBatchRepository(session)
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    id = batch_services.add_batch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
        repo, session
    )
    return jsonify({'id': str(id)}), 201

@app.route("/batch/<id>", methods=['GET'])
def get_batch(id):
    session = get_session()
    repo = batch_repository.SqlAlchemyBatchRepository(session)
    batch = batch_services.get_batch(id,repo)
    return jsonify(batch.as_dict()), 200

@app.route("/batches", methods=['GET'])
def get_batches():
    session = get_session()
    repo = batch_repository.SqlAlchemyBatchRepository(session)
    batches = [batch.as_dict() for batch in batch_services.get_batches(repo)]
    return jsonify(batches), 200

@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    session = get_session()
    repo = batch_repository.SqlAlchemyBatchRepository(session)
    line = OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )
    try:
        batchref = batch_services.allocate(line, repo, session)
    except (OutOfStock, batch_services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


