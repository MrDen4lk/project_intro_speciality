import csv
import os
import aiohttp
import json
from dotenv import load_dotenv
from parser.make_csv import data

# получение данных из dotenv
load_dotenv()

class Parser():

    def __init__(self, params, is_static):
        # Токен обновлять раз в две недели
        self.hh_api_token = os.getenv("HH_TOKEN")
        self.url = os.getenv("HH_URL")
        self.headers = {
            'Authorization': f'Bearer {self.hh_api_token}',
            'User-Agent': 'Python/requests',
            'Accept': 'application/json'
        }
        self.base_params = Parser.make_params(self, params)
        self.is_static = is_static
        self.per_page = params['per_page']

    def make_params(self, base_params : dict) -> dict: #работа с None
        new_params = dict()
        new_params['area'] = base_params['area']
        if base_params['text'] is not None:
            new_params['text'] = base_params['text']
        if base_params['experience'] is not None:
            new_params['experience'] = base_params['experience']
        if base_params['employment'] is not None:
            new_params['employment'] = base_params['employment']
        if base_params['sort'] is not None:
            new_params['sort'] = base_params['sort']
        return new_params


    # Получение json со страницы
    async def fetch_vacancies(self, session, url : str, params : dict) -> json:
        async with session.get(url, params=params, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()

    #
    async def fetch_all_vacancies(self, page_num : int) -> tuple[list[dict], int]:
        async with aiohttp.ClientSession() as session: # <- постоянное соединение с сервером
            total_vacancies = 0
            paramet = self.base_params.copy()
            paramet['page'] = page_num
            data = await (Parser.fetch_vacancies(self, session, self.url, paramet))
            all_vacancies = []

            try:
                    total_vacancies = data.get('found', 0)
                    all_vacancies.extend(data.get('items', []))

            except aiohttp.ClientResponseError as http_err:
                print(f"HTTP ошибка произошла: {http_err.status} - {http_err.message}")
            except Exception as err:
                print(f"Произошла ошибка: {err}")

            return all_vacancies, total_vacancies

    async def main(self, page_number : int) -> dict or csv: # <- возвращает json с вакансиями или csv
        # page_number - номер страницы которую нужно обработать (индексация с 0)
        vacancies = await Parser.fetch_all_vacancies(self, page_number)
        if self.is_static:
            static_vacancies = []
            static_vacancies.extend(vacancies[0])
            total_vacancies = vacancies[1]
            #максимум можно получить 2000 вакансий
            if total_vacancies > 2000:
                total_vacancies = 2000
            if total_vacancies > 300:
                total_vacancies = total_vacancies // 2

            #цикл по страницам
            page_number_iterator = 1
            while len(static_vacancies) < total_vacancies:
                vac = await Parser.fetch_all_vacancies(self, page_number_iterator)
                static_vacancies.extend(vac[0])
                page_number_iterator += 1
            #data превращает list[json] в csv
            return data(static_vacancies)
        else:
            return vacancies[0]

if __name__ == '__main__':
    params = { # например
            'area': 113,
            'text': 'Водитель',
            'per_page': 50,
            'only_with_salary': None,
            'experience' : None,
            'employment': None,
            'sort': None
        }
    k = Parser(params, True)
    # True - статистика по вакансиям (csv), False - вакансии