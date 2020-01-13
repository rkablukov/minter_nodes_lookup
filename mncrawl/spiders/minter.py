# -*- coding: utf-8 -*-
import os
import scrapy
import json
from urllib.parse import urlparse, urljoin
from mncrawl.items import NodeItem, ConnectionItem, NodeStatusItem

from sqlalchemy.orm import sessionmaker
from mncrawl.models import NodeStatus, db_connect, create_table


class MinterSpider(scrapy.Spider):
    name = 'minter'
    # allowed_domains = ['api.minter.one']
    # start_urls = ['https://api.minter.one/net_info']

    def __init__(self):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        rs = session.query(NodeStatus.api_url).filter(NodeStatus.api == True).all()
        self.start_urls = ['%s/net_info' % x[0] for x in rs]
        session.close()

        if len(self.start_urls) == 0:
            self.start_urls = ['http://116.202.85.179:8841/net_info']

    def parse(self, response):
        j = json.loads(response.text)
        if not 'result' in j:
            return

        parsed_uri = urlparse(response.url)
        node_ip = parsed_uri.hostname
        api_url = urljoin(response.url, '/')
        yield NodeItem(ip=node_ip)

        yield NodeStatusItem(
            ip=node_ip,
            api=True,
            api_url=api_url,
            full_node=False     # Статус full_node тут неизвестен
        )

        # Чекаем запрос full_node
        yield scrapy.Request(
            urljoin(api_url, '/coin_info?symbol=BTCSECURE&height=1000'), 
            callback=self.parse_full_node_response
        )

        peers = j['result']['peers']
        for peer in peers:
            remote_ip = peer['remote_ip']
            yield NodeItem(ip=remote_ip)

            yield NodeStatusItem(
                ip=remote_ip,
                api=False,          # Статус api тут неизвестен
                api_url='',
                full_node=False     # Статус full_node тут неизвестен
            )

            # Сохраняем данные
            yield ConnectionItem(
                ip_from=node_ip,
                ip_to=remote_ip
            )
            # Добавляем новые запросы
            urls = [x % remote_ip for x in [
                'http://%s:8841/net_info',
                'http://%s/net_info',
                'https://%s/net_info'
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