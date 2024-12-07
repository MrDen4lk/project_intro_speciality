import csv
import io
import pandas as pd
from dask.dataframe import DataFrame
from aiogram import types




async def data(vac_list : list[dict]) -> csv:
    #Создаём lists для хранения значений и дальнейшей передачи их в csv
    name_list = [0] * len(vac_list)
    employer_list = [0] * len(vac_list)
    employment_list = [0] * len(vac_list)
    city_list = [0] * len(vac_list)
    experience_list = [0] * len(vac_list)
    salary_from_list = [0] * len(vac_list)
    salary_to_list = [0] * len(vac_list)
    i = 0
    #Добавляем признаки в lists
    for vac in vac_list:
        salary = vac.get('salary')
        salary_from = 'None'
        salary_to = 'None'
        if salary:
            salary_from = salary.get('from')
            salary_to = salary.get('to')
        name_list[i] = (vac.get("name"))
        employer_list[i] = (vac.get('employer', {}).get('name'))
        employment_list[i] = (vac.get("employment", {}).get("name"))
        experience_list[i] = (vac.get("experience", {}).get("name"))
        city_list[i] = (vac.get("area", {}).get("name"))
        salary_from_list[i] = salary_from
        salary_to_list[i] = salary_to
        i += 1
    #Создаём dataframe
    df = pd.DataFrame({"Профессия": name_list, "Компания": employer_list,
                       "Занятость": employment_list, "Город": city_list,
                       "Опыт": experience_list, "зп_от": salary_from_list,
                       "зп_до": salary_to_list})
    #Отправляем csv
    csv_file_path = "data.csv"
    df.to_csv(csv_file_path, index=False)
    with open(csv_file_path, 'rb') as file:
        await bot.send() #здесь допиши что и куда
    os.remove(csv_file_path)
