from flask import Blueprint, jsonify
from mnlookup.mainapp.database import Session, NodeStatus


api = Blueprint('api', __name__)


@api.route('/api_nodes', methods=['GET'])
def api_nodes():
    session = Session()

    rs = session.query(NodeStatus.api_url).filter_by(api=1).all()

    api_urls = [x[0] for x in rs]

    return jsonify(api_urls)


@api.route('/full_nodes', methods=['GET'])
def full_nodes():
    session = Session()

    rs = session.query(NodeStatus.api_url).filter_by(full_node=1).all()

    api_urls = [x[0] for x in rs]

    return jsonify(api_urls)