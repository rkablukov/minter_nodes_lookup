Minter Nodes Crawl
==================

УСТАНОВКА
---------

      git clone https://github.com/rkablukov/mncrawl.git
      cd mccrawl
      pipenv --three
      pipenv install -r requirements.txt

Так же необходимо получить ключ Api на сайте https://geoipify.whoisxmlapi.com/api и указать его в переменной окружения API_KEY.

ЗАПУСК ПАУКА
------------

      pipenv shell
      scrapy crawl minter -o connections.json

Во время работы паук заполняет следующие файлы:
* ips.txt - ip адреса нод
* geoips.txt - информация о геолокации нод
* connections.json - связи нод. В поле from нода с открытым api

ГЕНЕРАЦИЯ КАРТЫ
---------------

      python plot2map.py

В результате получаем файл minter_nodes.html
