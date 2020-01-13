from datetime import datetime
from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)

from scrapy.utils.project import get_project_settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))

def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class Node(DeclarativeBase):
    __tablename__ = "node"

    #id = Column(Integer, primary_key=True)

    ip = Column('ip', String(30), primary_key=True)

    # location
    lon = Column('lon', Float)
    lat = Column('lat', Float)

    country = Column('country', String(2))
    region = Column('region', String(100))
    city = Column('city', String(100))
    postal_code = Column('postal_code', String(10))
    timezone = Column('timezone', String(10))
    geoname_id = Column('geoname_id', Integer)

    # AS
    as_asn = Column('as_asn', Integer)
    as_name = Column('as_name', String(100))
    as_route = Column('as_route', String(100))
    as_domain = Column('as_domain', String(100))
    as_type = Column('as_type', String(10))

    isp = Column('isp', String(100))


class NodeConnection(DeclarativeBase):
    __tablename__ = 'connection'

    ip_from = Column('ip_from', String(30), primary_key=True)
    ip_to = Column('ip_to', String(30), primary_key=True)

    updated = Column('updated', DateTime, default=datetime.now, onupdate=datetime.now)


class NodeStatus(DeclarativeBase):
    __tablename__ = 'node_status'

    ip = Column('ip', String(30), primary_key=True)

    api = Column('api', Boolean, default=False)
    api_url = Column('api_url', Text)
    full_node = Column('full_node', Boolean, default=False)

    updated = Column('updated', DateTime, default=datetime.now, onupdate=datetime.now)
    api_checked = Column('api_checked', DateTime, default=datetime(1900,1,1))
    full_node_checked = Column('full_node_checked', DateTime, default=datetime(1900,1,1))


class NodeHistory(DeclarativeBase):
    __tablename__ = 'node_history'

    date = Column('date', DateTime, default=datetime.now, primary_key=True)
    nodes = Column('nodes', Integer)
    api_nodes = Column('api_nodes', Integer)
    full_nodes = Column('full_nodes', Integer)
