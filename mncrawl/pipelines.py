# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
from datetime import datetime, timedelta
from sqlalchemy import func, case
from sqlalchemy.sql import select, insert, exists
from sqlalchemy.orm import sessionmaker
from mncrawl.models import (Node, NodeConnection, NodeStatus, NodeHistory,
                            db_connect, create_table)
from mncrawl.items import NodeItem, ConnectionItem, NodeStatusItem, NodeStatusExtendedItem

from simple_geoip import GeoIP


class NodePipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        # create_table(engine)
        self.Session = sessionmaker(bind=engine)

        # geoip
        API_KEY = os.environ.get('API_KEY', False)
        if not API_KEY:
            raise Exception('API_KEY has not been defined.')
        self.geoip = GeoIP(API_KEY)

        # start time
        self.start_time = datetime.now() - timedelta(minutes=1)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        session = self.Session()

        try:
            # delete not relevant connection
            session.query(NodeConnection).filter(
                NodeConnection.updated < self.start_time
            ).delete()

            # удаляем неактивные ноды
            session.query(NodeStatus).filter(
                NodeStatus.updated < self.start_time
            ).delete()

            # убираем статус api ноды, где теперь нет api
            session.query(NodeStatus).filter(
                NodeStatus.api_checked < self.start_time
            ).update({
                'api': False,
                'api_url': '',
                'api_checked': datetime.now()
            })

            # убираем статус full_node, где нет full_node
            session.query(NodeStatus).filter(
                NodeStatus.full_node_checked < self.start_time
            ).update({
                'full_node': False,
                'full_node_checked': datetime.now()
            })

            # Добавляем историческую информациюю статистики
            nht = NodeHistory.__table__
            sel = session.query(
                func.count(NodeStatus.ip),
                func.count(case([(NodeStatus.api, 1)])),
                func.count(case([(NodeStatus.full_node, 1)]))
            )
            ins = nht.insert().from_select(
                (NodeHistory.nodes, NodeHistory.api_nodes, NodeHistory.full_nodes),
                sel
            )
            session.execute(ins)

            # commiting
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def process_item(self, item, spider):
        if isinstance(item, NodeItem):
            self.handle_node(item, spider)
        if isinstance(item, ConnectionItem):
            self.handle_connection(item, spider)
        if isinstance(item, NodeStatusItem):
            self.handle_status(item, spider)
        if isinstance(item, NodeStatusExtendedItem):
            self.handle_status(item, spider)

        return item

    def handle_node(self, item, spider):
        session = self.Session()

        node = session.query(Node).filter_by(
            ip=item['ip']).first()

        if node is None:
            node = Node(ip=item['ip'])

            geodata = self.geoip.lookup(item['ip'])

            for k, v in geodata['location'].items():
                if k == 'lng':
                    node.lon = v
                elif k == 'postalCode':
                    node.postal_code = v
                elif k == 'geonameId':
                    node.geoname_id = v
                else:
                    setattr(node, k,  v)
            for k, v in geodata['as'].items():
                setattr(node, 'as_%s' % k, v)
            node.isp = geodata['isp']

            try:
                session.add(node)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

        else:
            session.close()

    def handle_connection(self, item, spider):
        session = self.Session()

        nc = session.query(NodeConnection).filter_by(
            ip_from=item['ip_from'], ip_to=item['ip_to']
        ).first()

        if nc is None:
            # создаём новую запись
            nc = NodeConnection()
            nc.ip_from = item['ip_from']
            nc.ip_to = item['ip_to']

            try:
                session.add(nc)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

        elif nc.updated < self.start_time:
            # обновляем запись
            try:
                session.query(NodeConnection).filter_by(
                    ip_from=item['ip_from'], ip_to=item['ip_to']
                ).update(item, synchronize_session=False)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

        else:
            session.close()

    def handle_status(self, item, spider):
        session = self.Session()

        status = session.query(NodeStatus).filter_by(
            ip=item['ip']
        ).first()

        if status is None:
            status = NodeStatus(
                ip=item['ip'],
                api=item['api'],
                api_url=item['api_url'],
                full_node=item['full_node']
            )

            # установим атрибуты node_info
            if isinstance(item, NodeStatusExtendedItem):
                status.set_node_info(item)

            if status.api:
                status.api_checked = datetime.now()

            if status.full_node:
                status.full_node_checked = datetime.now()

            try:
                session.add(status)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
                return

        data = {
            'updated': datetime.now()
        }
        if item['api']:
            data = {
                'api': True,
                'api_url': item['api_url'],
                'api_checked': datetime.now()
            }

        if item['full_node']:
            data['full_node'] = True
            data['full_node_checked'] = datetime.now()

        if isinstance(item, NodeStatusExtendedItem):
            data['protocol_version_p2p'] = item['protocol_version_p2p']
            data['protocol_version_block'] = item['protocol_version_block']
            data['protocol_version_app'] = item['protocol_version_app']

            data['node_id'] = item['node_id']
            data['listen_addr'] = item['listen_addr']
            data['network'] = item['network']
            data['version'] = item['version']
            data['channels'] = item['channels']
            data['moniker'] = item['moniker']
            data['tx_index'] = item['tx_index']
            data['rpc_address'] = item['rpc_address']

        if data:
            try:
                session.query(NodeStatus).filter_by(
                    ip=item['ip']
                ).update(data, synchronize_session=False)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()
