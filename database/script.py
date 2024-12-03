# Вытаскивает список городов и их id

import requests
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

def get_cities() -> json:
    url = os.getenv("HH_URL_AREAS")
    response = requests.get(url)

    if response.status_code == 200:
        areas_data = response.json()
        cities_dict = {}
        # Функция для рекурсивного прохода по дереву областей
        def parse_areas(areas):
            for area in areas:
                if 'areas' in area and area['areas']:
                    parse_areas(area['areas'])
                else:
                    area_name = str(area['name'])
                    if area_name.count("(") != 0:
                        area_name = area_name[:area_name.find("(")]
                    cities_dict[area_name] = int(area['id'])

        # Начинаем обработку с корневых элементов
        parse_areas(areas_data)
        return cities_dict

    else:
        print({response.status_code})
        return {}

if __name__ == "__main__":
    #cities_dict = get_cities()
    #with open("inp.txt", "w") as inp:
    #    inp.write(json.dumps(cities_dict, ensure_ascii=False, indent=4))
    pass
