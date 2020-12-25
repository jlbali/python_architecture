from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from domain.order_line import OrderLine
from domain.exceptions import OutOfStock
import adapters.orm as orm
import adapters.repository_batch as batch_repository
import service_layer.batch_services as batch_services


orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)

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


