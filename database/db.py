# данные городов
list_of_towns = ["Moscow", "Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan", "Nizhny", "other"]
map_of_towns = {"Moscow": "Москва",
                "Petersburg": "Санкт-Петербург",
                "Novosibirsk" : "Новосибирск",
                "Yekaterinburg" : "Екатеринбург",
                "Kazan" : "Казань",
                "Nizhny" : "Нижний Новгород",
                "other": "Другой"
                }

# данный только ЗП
list_of_salary = ["yes", "no"]
map_of_salary = {"yes" : "Да",
                 "no" : "Нет"
                }

# данные опыта
list_of_experience = ["noexp", "1to3", "3to6", "more6"]
map_of_experience = {"noexp": "Без опыта",
                     "1to3": "От 1 до 3 лет",
                     "3to6" : "От 3 до 6 лет",
                     "more6" : "Больше 6 лет"
                    }

# данные графика
list_of_employment = ["full", "part", "project", "probation"]
map_of_employment = {"full": "Полный",
                     "part": "Неполный",
                     "project" : "Проектный",
                     "probation" : "Испытательный срок"
                    }

# номер города для парсера
update_for_req_town = {
  "Москва": 1,
  "Санкт-Петербург": 2,
  "Новосибирск": 3,
  "Екатеринбург": 4,
  "Казань": 5,
  "Нижний Новгород": 6,
  "Челябинск": 7,
  "Самара": 8,
  "Омск": 9,
  "Ростов-на-Дону": 10,
  "Уфа": 11,
  "Красноярск": 12,
  "Воронеж": 13,
  "Пермь": 14,
  "Волгоград": 15
}

update_for_req_salary = {
    "Да" : "True",
    "Нет" : "False"
}

update_for_req_exp = {
    "Без опыта" : "noExperience",
    "От 1 до 3 лет" : "between1And3",
    "От 3 до 6 лет" : "between3And6",
    "Больше 6 лет" : "moreThan6"
}

update_for_empl = {
    "Полный" : "full",
    "Неполный" : "part",
    "Проектный" : "project",
    "Испытательный срок" : "probation"
}

users = {

}