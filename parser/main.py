import asyncio
import os
import time

import requests
import aiohttp
import logging
import json
from dotenv import load_dotenv
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
        self.base_params = params
        self.is_static = is_static
        self.per_page = params['per_page']

    def make_params(self):
        text = 'text'
        experience = 'experience'
        only_with_salary = 'only_with_salary'
        employment = 'employment'
        sort = 'sort'

        if self.base_params['area'] == False:
            self.base_params['area'] = 113
        if self.base_params['text'] == False:
            text = 'NONE_text'
        if self.base_params['text'] == False:
            text = 'NONE_text'
        if self.base_params['text'] == False:
            text = 'NONE_text'
        if self.base_params['text'] == False:
            text = 'NONE_text'

        new_params = {  # например
            'area': self.base_params['area'],
            text : self.base_params['text'],
            'per_page': self.base_params['per_page'],
            only_with_salary: self.base_params['only_with_salary'],
            experience: self.base_params['experience'],
            employment: self.base_params['employment'],
            sort: self.base_params['sort'],
        }


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


    def display_vacancies(self, vacancies): # Просто для просмотра
        for vacancy in vacancies:
            title = vacancy.get('name')
            employer = vacancy.get('employer', {}).get('name')
            salary = vacancy.get('salary')
            url_vacancy = vacancy.get('alternate_url')
            if salary:
                salary_from = salary.get('from')
                salary_to = salary.get('to')
                currency = salary.get('currency')
                if salary_from and salary_to:
                    salary_info = f"{salary_from} - {salary_to} {currency}"
                elif salary_to and not (salary_from):
                    salary_info = f"До {salary_to} {currency}"
                elif salary_from and not (salary_to):
                    salary_info = f"От {salary_from} {currency}"
            else:
                salary_info = "Не указана"

            print(f"Название: {title}")
            print(f"Компания: {employer}")
            print(f"Зарплата: {salary_info}")
            print(f"Ссылка: {url_vacancy}\n")

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
            for page_number_iterator in range(1, total_vacancies // self.per_page):
                vac = await Parser.fetch_all_vacancies(self, page_number_iterator)
                static_vacancies.extend(vac[0])
            return static_vacancies
        else:
            return vacancies

if __name__ == '__main__':
    #1
    # params передаётся парсеру
    experience = 'experience'
    only_with_salary = 'only_with_salary'
    employment = 'employment'
    sort = 'sort'

    params = { # например
            'area': 1,
            'text': 'Водитель',
            'per_page': 50,
            only_with_salary: "False",
            experience : None,
            employment: "full",
            sort: "relevance"
        }
    k = Parser(params, True)
    #print(asyncio.run(k.main(0)))
    print(len(asyncio.run(k.main(0))))

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