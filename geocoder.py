import os
import sys

import pygame
import requests

API_KEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def geocode(address):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"
    }
    resp = requests.get(geocoder_request, params=geocoder_params)
    if resp:
        json_response = resp.json()
    else:
        raise RuntimeError(
            f"Ошибка выполнения запроса {geocoder_request} - {resp.status_code}, {resp.reason}")
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def get_coords(address):
    toponym = geocode(address)
    if not toponym:
        return None, None
    toponym_coords = toponym["Point"]["pos"]
    return list(map(lambda x: float(x), toponym_coords.split(" ")))


def get_ll_span(address):
    toponym = geocode(address)
    toponym_long, toponym_lat = get_coords(address)
    ll = ",".join(map(lambda x: str(x), [toponym_long, toponym_lat]))
    envelope = toponym["boundedBy"]["Envelope"]
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")
    dx = abs(float(l) - float(r)) / 2
    dy = abs(float(l) - float(r)) / 2
    span = f"{dx},{dy}"
    return ll, span


def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = f"http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}"
    else:
        map_request = f"http://static-maps.yandex.ru/1.x/?l={map_type}"

    if add_params:
        map_request += "&" + add_params
    resp = requests.get(map_request)
    if not resp:
        raise RuntimeError(
            f"Ошибка выполнения запроса {map_request} - {resp.status_code}, {resp.reason}")
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(resp.content)
    except IOError as e:
        print(f"Ошибка записи файла: {e}")
        sys.exit(2)
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()
    os.remove(map_file)
