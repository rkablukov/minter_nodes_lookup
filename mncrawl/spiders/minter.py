# -*- coding: utf-8 -*-
import os
import scrapy
import json
from urllib.parse import urlparse, urljoin
from mncrawl.items import NodeItem, ConnectionItem, NodeStatusItem, NodeStatusExtendedItem

from sqlalchemy.orm import sessionmaker
from mncrawl.models import NodeStatus, db_connect, create_table


class MinterSpider(scrapy.Spider):
    name = 'minter'
    # allowed_domains = ['api.minter.one']
    # start_urls = ['https://api.minter.one/net_info']

    def __init__(self):
        self.minter_network = os.environ.get('MINTER_NETWORK')
        self.minter_api_node = os.environ.get('MINTER_API_NODE')

        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        rs = session.query(NodeStatus.api_url).filter(NodeStatus.api == True).all()
        self.start_urls = ['%s/status' % x[0] for x in rs]
        session.close()

        if len(self.start_urls) == 0:
            #self.start_urls = ['http://116.202.85.179:8841/status']
            self.start_urls = ['%s/status' % self.minter_api_node]

    def parse(self, response):
        j = json.loads(response.text)
        if not 'result' in j:
            return
        
        parsed_uri = urlparse(response.url)
        node_ip = parsed_uri.hostname
        api_url = urljoin(response.url, '/')
        yield NodeItem(ip=node_ip)

        node_info = j['result']['tm_status']['node_info']

        # сканим только ноды указанной сети
        if node_info['network'] != self.minter_network:
            return

        yield NodeStatusExtendedItem(
            ip=node_ip,
            api=True,
            api_url=api_url,
            full_node=False,     # Статус full_node тут неизвестен

            protocol_version_p2p=node_info['protocol_version']['p2p'],
            protocol_version_block=node_info['protocol_version']['block'],
            protocol_version_app=node_info['protocol_version']['app'],

            node_id=node_info['id'],
            listen_addr=node_info['listen_addr'],
            network=node_info['network'],
            version=node_info['version'],
            channels=node_info['channels'],
            moniker=node_info['moniker'],
            tx_index=node_info['other']['tx_index'],
            rpc_address=node_info['other']['rpc_address']
        )

        # Чекаем запрос full_node
        yield scrapy.Request(
            urljoin(api_url, '/coin_info?symbol=BTCSECURE&height=1000'), 
            callback=self.parse_full_node_response
        )

        yield scrapy.Request(
            urljoin(api_url, '/net_info'), 
            callback=self.parse_net_info
        )
        

    def parse_net_info(self, response):
        j = json.loads(response.text)
        if not 'result' in j:
            return

        parsed_uri = urlparse(response.url)
        node_ip = parsed_uri.hostname
        #api_url = urljoin(response.url, '/')

        peers = j['result']['peers']
        for peer in peers:
            remote_ip = peer['remote_ip']
            yield NodeItem(ip=remote_ip)

            node_info = peer['node_info']

            yield NodeStatusExtendedItem(
                ip=remote_ip,
                api=False,          # Статус api тут неизвестен
                api_url='',
                full_node=False,     # Статус full_node тут неизвестен

                protocol_version_p2p=node_info['protocol_version']['p2p'],
                protocol_version_block=node_info['protocol_version']['block'],
                protocol_version_app=node_info['protocol_version']['app'],

                node_id=node_info['id'],
                listen_addr=node_info['listen_addr'],
                network=node_info['network'],
                version=node_info['version'],
                channels=node_info['channels'],
                moniker=node_info['moniker'],
                tx_index=node_info['other']['tx_index'],
                rpc_address=node_info['other']['rpc_address']
            )

            # Сохраняем данные
            yield ConnectionItem(
                ip_from=node_ip,
                ip_to=remote_ip
            )
            # Добавляем новые запросы
            urls = [x % remote_ip for x in [
                'http://%s:8841/status',
                'http://%s/status',
                'https://%s/status'
            ]]
            for url in urls:
                yield scrapy.Request(url, callback=self.parse)

    def parse_full_node_response(self, response):
        j = json.loads(response.text)
        if not 'result' in j:
            return
        
        parsed_uri = urlparse(response.url)
        node_ip = parsed_uri.hostname
        api_url = urljoin(response.url, '/')

        yield NodeStatusItem(
            ip=node_ip,
            api=True,
            api_url=api_url,
            full_node=True
        )