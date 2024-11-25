import asyncio
import os
import requests
from dotenv import load_dotenv
import aiohttp
import logging

load_dotenv()

class Parser():

    def __init__(self, params):
        # Токен обновлять раз в две недели
        self.hh_api_token = os.getenv("HH_TOKEN")
        self.url = os.getenv("HH_URL")
        self.headers = {
            'Authorization': f'Bearer {self.hh_api_token}',
            'User-Agent': 'Python/requests',
            'Accept': 'application/json'
        }
        self.base_params = params

    # Получение json со страницы
    async def fetch_vacancies(self, session, url, params):
        async with session.get(url, params=params, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()

    #
    async def fetch_all_vacancies(self, page_num):
        async with aiohttp.ClientSession() as session: # <- постоянное соединение с сервером
            tasks = [] # <- получение json по страницам
            paramet = self.base_params.copy()
            paramet['page'] = page_num
            tasks.append(Parser.fetch_vacancies(self, session, self.url, paramet))
            all_vacancies = []

            try:
                responses = await asyncio.gather(*tasks)
                for data in responses:
                    all_vacancies.extend(data.get('items', []))

            except aiohttp.ClientResponseError as http_err:
                print(f"HTTP ошибка произошла: {http_err.status} - {http_err.message}")
            except Exception as err:
                print(f"Произошла ошибка: {err}")

            return all_vacancies

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
        return vacancies

if __name__ == '__main__':
    #1
    # params передаётся парсеру
    params = { # например
            'area': 1,
            'text': "ML engineer",
            'per_page': 50,
            'only_with_salary': "True",
            'experience': "between3And6",
            'employment': "full",
            'sort': "publication_time"
        }
    k = Parser(params)
    asyncio.run(k.main(0))

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