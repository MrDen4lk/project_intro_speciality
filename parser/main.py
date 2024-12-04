import asyncio
import os
import time

import requests
import aiohttp
import logging
import json
import pandas as pd
from dotenv import load_dotenv
from make_csv import data
#proverka

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

    def make_params(self, base_params):
        new_params= {}
        if base_params['text'] != "None":
            new_params['text'] = base_params['text']
        if base_params['experience'] != "None":
            new_params['experience'] = base_params['experience']
        if base_params['only_with_salary'] == "None":
            new_params['only_with_salary'] = "False"
        if base_params['employment'] != "None":
            new_params['employment'] = base_params['employment']
        if base_params['sort'] != "None":
            new_params['sort'] = base_params['sort']
        return new_params


    # Получение json со страницы
    async def fetch_vacancies(self, session, url, params):
        async with session.get(url, params=params, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()

    #
    async def fetch_all_vacancies(self, page_num):
        async with aiohttp.ClientSession() as session: # <- постоянное соединение с сервером
            total_vacancies = 0
            tasks = [] # <- получение json по страницам
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

    async def main(self, page_number): # <- возвращает json с вакансиями
        # page_number - номер страницы которую нужно обработать (индексация с 0)
        # Если указать per_page = 100 page = 1, то необязательно на одной странице будет 100 вакансий
        # (Чем больше количество получаемых вакансий, тем больше нудно времени на работу парсера)
        # (Если total_page = 1, можно не ставить time.sleep (наверное)
        # !!! если bad request 400, то поставь time.sleep(~0.1))
        vacancies = await Parser.fetch_all_vacancies(self, page_number)
        #Parser.display_vacancies(self, vacancies)
        if self.is_static:
            static_vacancies = []
            static_vacancies.extend(vacancies[0])
            total_vacancies = vacancies[1]
            if total_vacancies > 2000:
                total_vacancies = 2000
            page_number_iterator = 1
            while len(static_vacancies) < total_vacancies:
                vac = await Parser.fetch_all_vacancies(self, page_number_iterator)
                static_vacancies.extend(vac[0])
                page_number_iterator += 1
            return data(static_vacancies)
        else:
            return vacancies

if __name__ == '__main__':
    #1
    # params передаётся парсеру

    params = { # например
            'area': 113,
            'text': 'Водитель',
            'per_page': 50,
            'only_with_salary': "None",
            'experience' : "None",
            'employment': "None",
            'sort': "None"
        }
    k = Parser(params, True)
    #print(asyncio.run(k.main(0)))
    print(asyncio.run(k.main(0)))

#1
# area (Москва - 1, Санкт-Петербург - 2 и тд) https://github.com/hhru/api/blob/master/docs/areas.md

# text (Можно писать любую профессию, поиск более менее умный)

# per_page - количество вакансий просматриваемых на странице

# only_with_salary (С указанием зарплаты - "True", без - "False")

# experience ("noExperience", "between1And3", "between3And6", "moreThan6")

# employment ("full", "part", "project", "probation" - испытательный срок)

# sort (
    # "relevance" - сортировка по релевантности,
    # "publication_time" - сортировка по времени публикации,
    # "salary_desc" - сортировка по заработной плате по убыванию,
    # "salary_asc" - сортировка по заработной плате по возрастанию
# )

# api.hh.ru есть другие параметры