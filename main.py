import sys
from io import BytesIO
# Этот класс поможет нам сделать картинку из потока байт

import requests
from PIL import Image

from distance import lonlat_distance

address_ll = sys.argv[1]
print(address_ll)

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

search_params = {
    "apikey": api_key,
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    # ...
    pass
print(response.url)
# Преобразуем ответ в json-объект
json_response = response.json()

# Получаем первую найденную организацию.
organization = json_response["features"][0]
# Название организации.
org_name = organization["properties"]["CompanyMetaData"]["name"]
# Адрес организации.
org_address = organization["properties"]["CompanyMetaData"]["address"]

# Получаем координаты ответа.
point = organization["geometry"]["coordinates"]
org_point = "{0},{1}".format(point[0], point[1])
x = list(map(float, address_ll.split(',')))
y = list(map(float, org_point.split(',')))

snippet = {}
snippet["address"] = org_address
snippet["name"] = org_name
snippet["hours"] = organization["properties"]["CompanyMetaData"]["Hours"]["Availabilities"]
snippet["distance"] = lonlat_distance(x, y)
print(snippet)

delta = str(max(abs(x[0] - y[0]), abs(x[1] - y[1])) * 2)

# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    "ll": address_ll,
    "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": "{0},pm2dgl".format(org_point)
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
print(response.url)

Image.open(BytesIO(
    response.content)).show()

# Создадим картинку
# и тут же ее покажем встроенным просмотрщиком операционной системы
