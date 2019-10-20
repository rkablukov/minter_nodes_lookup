# -*- coding: utf-8 -*-
import json
from gmplot import gmplot

# Инициализируем карту в указанной точке
gmap = gmplot.GoogleMapPlotter(50.567564, 22.679136, 3)

geoips = {}

# Добавляем маркеры
with open('geoips.txt', 'r') as f:
    for line in f:
        line = line.replace("'", "\"")
        line = line.replace("Oblast\"\"", "Oblast'\"")
        line = line.replace("\"ER-Telecom Holding\"", "'ER-Telecom Holding'")
        #print(line)
        j = json.loads(line)
        ip = j['ip']
        lat = j['location']['lat']
        lng = j['location']['lng']
        geoips[ip] = {'lat': lat, 'lng': lng}
        print('%s: %s, %s' % (ip, lat, lng))
        gmap.marker(lat, lng, 'cornflowerblue', title=ip)

# Рисуем связи
with open('connections.json', 'r') as f:
    j = json.load(f)
    for conn in j:
        geofrom = geoips[conn['from']]
        geoto = geoips[conn['to']]
        if geofrom is None or geoto is None:
            continue
        latitude_list = [geofrom['lat'], geoto['lat']]
        longitude_list = [geofrom['lng'], geoto['lng']]
        gmap.plot(latitude_list, longitude_list,  
           'cornflowerblue', edge_width = 1)

# Генерируем html с картой Google
gmap.draw("minter_nodes.html")
