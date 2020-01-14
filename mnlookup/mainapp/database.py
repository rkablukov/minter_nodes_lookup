from sqlalchemy import func, case
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import concat
from mncrawl.models import Node, NodeStatus, NodeHistory, db_connect, create_table


engine = db_connect()
create_table(engine)
Session = sessionmaker(bind=engine)


def load_nodes():
    session = Session()
    rs = session.query(
        NodeStatus.ip, 
        Node.lat, 
        Node.lon,
        concat(Node.country, ", ", Node.city)
    ).join(Node, Node.ip == NodeStatus.ip).all()

    ip = [x[3] for x in rs]
    lat = [x[1] for x in rs]
    lng = [x[2] for x in rs]
    
    session.close()

    return ip, lat, lng


def load_countries():
    session = Session()
    rs = session.query(
        func.count(NodeStatus.ip), 
        Node.country
    ).join(Node, Node.ip == NodeStatus.ip
    ).group_by(Node.country
    ).order_by(func.count(NodeStatus.ip).desc()).all()
    #).order_by(func.count(NodeStatus.ip).desc()).limit(10).all()

    number_of_nodes = [x[0] for x in rs[:9]]
    countries = [x[1] for x in rs[:9]]

    number_of_others = sum([x[0] for x in rs[9:]])
    if number_of_others > 0:
        number_of_nodes += [number_of_others]
        countries += ["Others"]

    session.close()
    
    return countries, number_of_nodes


def load_ases():
    session = Session()
    rs = session.query(
        func.count(NodeStatus.ip), 
        Node.as_name
    ).join(Node, Node.ip == NodeStatus.ip
    ).group_by(Node.as_name
    ).order_by(func.count(NodeStatus.ip).desc()).all()
    #).order_by(func.count(NodeStatus.ip).desc()).limit(10).all()

    number_of_nodes = [x[0] for x in rs[:9]]
    ases = [x[1] for x in rs[:9]]

    number_of_others = sum([x[0] for x in rs[9:]])
    if number_of_others > 0:
        number_of_nodes += [number_of_others]
        ases += ["Others"]

    session.close()
    
    return ases, number_of_nodes


def load_stat():
    session = Session()
    rs = session.query(
        func.count(NodeStatus.ip),
        func.count(case([(NodeStatus.api, 1)])),
        func.count(case([(NodeStatus.full_node, 1)]))
    ).first()

    session.close()

    return rs[0], rs[1], rs[2]


def random_api_node():
    session = Session()
    rs = session.query(
        NodeStatus.api_url
    ).filter_by(
        api=True
    ).order_by(func.rand()).first()

    session.close()

    return rs[0]


def load_history():
    session = Session()
    rs = session.query(
        NodeHistory.date,
        NodeHistory.nodes
    ).order_by(NodeHistory.date).limit(10).all()

    session.close()

    dates = [x[0] for x in rs]
    nodes = [x[1] for x in rs]

    return dates, nodes
