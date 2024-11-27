import requests
import json

def get_cities() -> json:
    url = "https://api.hh.ru/areas"
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
                    cities_dict[area['name']] = int(area['id'])

        # Начинаем обработку с корневых элементов
        parse_areas(areas_data)
        return cities_dict

    else:
        print({response.status_code})
        return {}

if __name__ == "__main__":
    cities_dict = get_cities()
    with open("inp.txt", "w") as inp:
        inp.write(json.dumps(cities_dict, ensure_ascii=False, indent=4))
    #print(cities_dict['Москва'])