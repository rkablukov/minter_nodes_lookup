Minter Nodes Lookup
==================

Репозиторий содержит исходный код рабочего проекта [Minter Nodes Lookup](https://mnlookup.vemark.ru)


УСТАНОВКА
---------

      git clone https://github.com/rkablukov/minter_nodes_lookup.git
      cd minter_nodes_lookup
      pipenv --three
      pipenv install -r requirements.txt

Для работы приложения потребуется ключ API к сервису [IP Geolocation API](https://geoipify.whoisxmlapi.com/api) и указать его в переменной окружения API_KEY.

Так же потребуется ключ API к сервису [mapbox](https://account.mapbox.com), который должен быть записан в переменную окружения MAPBOX_ACCESS_TOKEN.

Кроме того, в переменных окружения требуется указать строку соединения с базой MySQL в следующем формате

      DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME?charset=utf8mb4

и текущее название сети Minter с URL API ноды, с которой паук начнёт сбор информации 

      MINTER_NETWORK=minter-mainnet-1
      MINTER_API_NODE=http://109.235.65.184:8841


ЗАПУСК ПРИЛОЖЕНИЯ
------------

Если все необходимые переменные окружения установлены или записаны в файл .env, то запустить приложение можно так:

      pipenv shell
      python ./manage.py runserver

Приложение собирает информацию о нодах раз в сутки в полночь.
