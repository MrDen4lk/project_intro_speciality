from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database.dynamic_db as ddb

# клавиатура для кнопки поиска в клавиатуре
start_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Искать🔎")]
])

# клавиатура для выбора города в сообщениях
async def inline_town_button() -> InlineKeyboardMarkup:
    town_button = InlineKeyboardBuilder() # создание конструктора для кнопки town
    for i in range(0, 6, 2):
        town_button.row(
            InlineKeyboardButton(text=(await ddb.get_town(str(i), "id")).value, callback_data=(await ddb.get_town(str(i), "id")).key),
            InlineKeyboardButton(text=(await ddb.get_town(str(i + 1), "id")).value, callback_data=(await ddb.get_town(str(i + 1), "id")).key)
        )
    town_button.row(InlineKeyboardButton(text="Другой", callback_data="other"))
    town_button.row(InlineKeyboardButton(text="Завершить поиск", callback_data="town_end"))
    return town_button.as_markup()

# клавиатура для выбранного города в сообщениях + ✅ у выбранного
async def inline_town_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    town_button_chosen = InlineKeyboardBuilder() # создание конструктора для кнопки town_chosen
    for i in range(0, 6, 2):
        data_1 = await ddb.get_town(str(i), "id")
        data_2 = await ddb.get_town(str(i + 1), "id")
        town_button_chosen.row(
            InlineKeyboardButton(text=data_1.value + ("✅" if chosen == data_1.key else ""),
                                          callback_data="pressed"),
            InlineKeyboardButton(text=data_2.value + ("✅" if chosen == data_2.key else ""),
                                 callback_data="pressed")
        )
    town_button_chosen.row(InlineKeyboardButton(text="Другой" + ("✅" if chosen == "other" else ""),
                                                callback_data="pressed"))
    if chosen == "town_end":
        town_button_chosen.row(InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed"))
    return town_button_chosen.as_markup()

# клавиатура для выбора только с ЗП в сообщениях
async def inline_salary_button() -> InlineKeyboardMarkup:
    salary_button = InlineKeyboardBuilder() # создание конструктора для кнопки salary
    for i in range(2):
        data = await ddb.get_salary(str(i), "id")
        salary_button.add(InlineKeyboardButton(text=data.value, callback_data=data.key))
    salary_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="salary_end"))
    return salary_button.adjust(2).as_markup()

# клавиатура для выбранной только с ЗП в сообщениях + ✅ у выбранного
async def inline_salary_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    salary_button_chosen = InlineKeyboardBuilder() # создание конструктора для кнопки salary_chosen
    for i in range(2):
        data = await ddb.get_salary(str(i), "id")
        if data.key == chosen:
            salary_button_chosen.add(InlineKeyboardButton(text=data.value + "✅", callback_data="pressed"))
        else:
            salary_button_chosen.add(InlineKeyboardButton(text=data.value, callback_data="pressed"))
    if chosen == "salary_end":
        salary_button_chosen.add(InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed"))
    return salary_button_chosen.adjust(2).as_markup()

# клавиатура для выбора опыта работы в сообщениях
async def inline_experience_button() -> InlineKeyboardMarkup:
    experience_button = InlineKeyboardBuilder() # создание конструктора для кнопки experience
    for i in range(4):
        data = await ddb.get_experience(str(i), "id")
        experience_button.add(InlineKeyboardButton(text=data.value, callback_data=data.key))
    experience_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="exp_end"))
    return experience_button.adjust(2).as_markup()

# клавиатура для выбранного опыта работы в сообщениях + ✅ у выбранного
async def inline_experience_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    experience_button_chosen = InlineKeyboardBuilder() # создание конструктора для кнопки experience_chosen
    for i in range(4):
        data = await ddb.get_experience(str(i), "id")
        if data.key == chosen:
            experience_button_chosen.add(InlineKeyboardButton(text=data.value + "✅", callback_data="pressed"))
        else:
            experience_button_chosen.add(InlineKeyboardButton(text=data.value, callback_data="pressed"))
    if chosen == "exp_end":
        experience_button_chosen.add(InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed"))
    return experience_button_chosen.adjust(2).as_markup()

# клавиатура для выбора графика работы в сообщениях
async def inline_employment_button() -> InlineKeyboardMarkup:
    employment_button = InlineKeyboardBuilder() # создание конструктора для кнопки employment
    for i in range(4):
        data = await ddb.get_employment(str(i), "id")
        employment_button.add(InlineKeyboardButton(text=data.value, callback_data=data.key))
    employment_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="empl_end"))
    return employment_button.adjust(2).as_markup()

# клавиатура для выбранного графика работы в сообщениях + ✅ у выбранного
async def inline_employment_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    employment_button_chosen = InlineKeyboardBuilder() # создание конструктора для кнопки employment_chosen
    for i in range(4):
        data = await ddb.get_employment(str(i), "id")
        if data.key == chosen:
            employment_button_chosen.add(InlineKeyboardButton(text=data.value + "✅", callback_data="pressed"))
        else:
            employment_button_chosen.add(InlineKeyboardButton(text=data.value, callback_data="pressed"))
    if chosen == "empl_end":
        employment_button_chosen.add(InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed"))
    return employment_button_chosen.adjust(2).as_markup()

# клавиатуры для выбора сортировки
async def inline_sort_button() -> InlineKeyboardMarkup:
    sort_button = InlineKeyboardBuilder() # создание конструктора для кнопки sort
    for i in range(4):
        data = await ddb.get_sort(str(i), "id")
        sort_button.add(InlineKeyboardButton(text=data.value, callback_data=data.key))
    sort_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="sort_end"))
    return sort_button.adjust(2).as_markup()

# клавиатура для выбранной сортировки + ✅ у выбранного
async def inline_sort_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    sort_button_chosen = InlineKeyboardBuilder() # создание конструктора для кнопки sort_chosen
    for i in range(4):
        data = await ddb.get_sort(str(i), "id")
        if data.key == chosen:
            sort_button_chosen.add(InlineKeyboardButton(text=data.value + "✅", callback_data="pressed"))
        else:
            sort_button_chosen.add(InlineKeyboardButton(text=data.value, callback_data="pressed"))
    if chosen == "sort_end":
        sort_button_chosen.add(InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed"))
    return sort_button_chosen.adjust(2).as_markup()

# клавиатура для выбора текста
async def inline_text() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить поиск", callback_data="text_end")]
    ])

# клавиатура при набранном тексте + ✅ у выбранного
async def inline_text_chosen(chosen: str) -> InlineKeyboardMarkup:
    if chosen == "text_end":
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed")]
    ])
    return InlineKeyboardMarkup(inline_keyboard=[])

# клавиатура для следующей/предыдущей вакансии
async def inline_pages_builder(user_id) -> InlineKeyboardMarkup:
    data = await ddb.get_user(user_id) # получение данных пользователя из БД
    inline_pages = InlineKeyboardBuilder() # создание конструктора для кнопки next/prev
    inline_pages.row(
        InlineKeyboardButton(text="<=", callback_data=("prev" if (data.vac_now != 1) else "pressed")),
        InlineKeyboardButton(text=str(data.vac_now)+"/"+str(data.vac_total), callback_data="pressed"),
        InlineKeyboardButton(text="=>", callback_data=("next" if (data.vac_now !=data.vac_total) else "pressed")))
    inline_pages.row(InlineKeyboardButton(text="Ещё", callback_data="morevac"))
    inline_pages.row(InlineKeyboardButton(text="Завершить поиск", callback_data="final_end"))

    return inline_pages.as_markup()

# клавиатура для выбранной вакансии + ✅ у выбранного
async def inline_pages_builder_chosen(user_id) -> InlineKeyboardMarkup:
    data = await ddb.get_user(user_id) # # создание конструктора для кнопки next/prev _chosen
    inline_pages = InlineKeyboardBuilder()
    inline_pages.add(InlineKeyboardButton(text="<=", callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text=str(data.vac_now)+"/"+str(data.vac_total), callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text="=>", callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text="Поиск завершен✅", callback_data="pressed"))
    return inline_pages.adjust(3).as_markup()