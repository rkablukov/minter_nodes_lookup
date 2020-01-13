import os
from subprocess import call


def run_spider():
    spider_name = "minter"
    call(['python', '-m', 'scrapy', 'crawl', spider_name])
