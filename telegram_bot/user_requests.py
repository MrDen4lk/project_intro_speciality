from parser.main import Parser
import database.dynamic_db as ddb

async def make_req(data: dict, page: int) -> list:
    # формирование данных для запроса
    req = {
        "area" : (await ddb.get_city(data["town"])).city_id,
        "text" : data["text"],
        "per_page" : 50,
        "only_with_salary" :(await ddb.get_salary(data["salary"], "value")).key,
        "experience" : (await ddb.get_experience(data["experience"], "value")).key,
        "employment" : (await ddb.get_employment(data["employment"], "value")).key,
        "sort" : (await ddb.get_sort(data["sort"], "value")).key
    }

    # отправка запроса и получение результата
    answer = Parser(req)
    back_return = []

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