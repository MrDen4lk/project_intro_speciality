from parser.main import Parser
import database.dynamic_db as ddb
import logging
import csv

# функция для обработки запросов пользователя на поиск вакансий и статистику
async def make_req(data: dict, page: int) -> list or csv:
    logging.info(data) # логирование полученных данных от пользователя

    # обработка полученных данных
    town = await ddb.get_city(data["town"])
    experience = (await ddb.get_experience(data["experience"], "value")).key
    employment = (await ddb.get_employment(data["employment"], "value")).key
    sort = (await ddb.get_sort(data["sort"], "value")).key if not data["search"] else None

    # формирование данных для запроса
    req = {
        "area": (town.city_id if town is not None else 113),
        "text": data["text"],
        "per_page" : 50,
        "only_with_salary": (await ddb.get_salary(data["salary"], "value")).key,
        "experience": (experience if experience != "any_exp" else None),
        "employment": (employment if employment != "any_empl" else None),
        "sort": (sort if sort != "any_sort" else None)
    }

    logging.info(req) # логирование данных запроса

    # отправка запроса и получение результата
    answer = Parser(req, data["search"])

    # проверка на тип запроса
    if data["search"]:
        return await answer.main(0)
    else:
        back_return = list()
        # форматирование полученных данных
        for req_answer in await answer.main(page):
            title = req_answer.get('name')
            employer = req_answer.get('employer', {}).get('name')
            salary = req_answer.get('salary')
            url_vacancy = req_answer.get('alternate_url')
            salary_info = ""
            if salary:
                salary_from = salary.get('from')
                salary_to = salary.get('to')
                currency = (salary.get('currency') if salary.get('currency') != "RUR" else "RUB")
                if salary_from and salary_to:
                    salary_info = f"{salary_from} - {salary_to} {currency}"
                elif salary_to and not salary_from:
                    salary_info = f"До {salary_to} {currency}"
                elif salary_from and not salary_to:
                    salary_info = f"От {salary_from} {currency}"
            else:
                salary_info = "Зарплата не указана"

            # формирование данных для return
            back_req = {
                "title" : title,
                "employer" : employer,
                "salary_info" : salary_info,
                "url" : url_vacancy,
            }
            back_return.append(back_req)

        return back_return
