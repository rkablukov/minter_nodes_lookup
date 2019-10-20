# -*- coding: utf-8 -*-
import os
import scrapy
import json
from urllib.parse import urlparse

from simple_geoip import GeoIP
API_KEY = os.environ.get('API_KEY', False)
if not API_KEY:
    raise Exception('API_KEY has not been defined.') 
geoip = GeoIP(API_KEY)


class MinterSpider(scrapy.Spider):
    name = 'minter'
    # allowed_domains = ['api.minter.one']
    # start_urls = ['https://api.minter.one/net_info']
    start_urls = ['https://51.83.230.173/net_info']
    unique_ips = set(line.strip() for line in open('ips.txt'))

    def add_ip_to_set(self, ip):
        if ip not in self.unique_ips:
            geodata = geoip.lookup(ip)
            self.unique_ips.add(ip)
            with open('ips.txt', 'a') as f:
                f.write('%s\n' % ip)
            with open('geoips.txt', 'a') as f:
                f.write('%s\n' % geodata)

    def parse(self, response):
        j = json.loads(response.text)
        if not 'result' in j:
            return

        parsed_uri = urlparse(response.url)
        node_ip = parsed_uri.hostname
        self.add_ip_to_set(node_ip)

        peers = j['result']['peers']
        for peer in peers:
            remote_ip = peer['remote_ip']
            self.add_ip_to_set(remote_ip)
            # Сохраняем данные
            yield {
                'from': node_ip,
                'to': remote_ip
            }
            # Добавляем новые запросы
            urls = [x % remote_ip for x in [
                'http://%s:8841/net_info',
                'http://%s/net_info',
                'https://%s/net_info'
            ]]
            for url in urls:
                yield scrapy.Request(url, callback=self.parse)
