from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import database.db as db

# клавиатура для кнопки поиска в клавиатуре
start_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Искать🔎")]
])

# клавиатура для выбора города в сообщениях
async def inline_town_button() -> InlineKeyboardMarkup:
    town_button = InlineKeyboardBuilder()
    for i in range(0, len(db.list_of_towns) - 1, 2):
        town_button.row(
            InlineKeyboardButton(text=db.map_of_towns[db.list_of_towns[i]], callback_data=db.list_of_towns[i]),
            InlineKeyboardButton(text=db.map_of_towns[db.list_of_towns[i + 1]], callback_data=db.list_of_towns[i + 1])
        )
    town_button.row(InlineKeyboardButton(text=db.map_of_towns[db.list_of_towns[-1]], callback_data=db.list_of_towns[-1]))
    town_button.row(InlineKeyboardButton(text="Завершить поиск", callback_data="town_end"))
    return town_button.as_markup()

# клавиатура для выбранного города в сообщениях
async def inline_town_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    town_button_chosen = InlineKeyboardBuilder()
    for i in range(0, len(db.list_of_towns) - 1, 2):
        town_button_chosen.row(
            InlineKeyboardButton(text=db.map_of_towns[db.list_of_towns[i]] + ("✅" if chosen == db.list_of_towns[i] else ""),
                                          callback_data="pressed"),
            InlineKeyboardButton(text=db.map_of_towns[db.list_of_towns[i + 1]] + ("✅" if chosen == db.list_of_towns[i + 1] else ""),
                                 callback_data="pressed")
        )
    town_button_chosen.row(InlineKeyboardButton(text=db.map_of_towns[db.list_of_towns[-1]] + ("✅" if chosen == db.list_of_towns[-1] else ""),
                                                callback_data="pressed"))
    if chosen == "town_end":
        town_button_chosen.row(InlineKeyboardButton(text="Завершить поиск✅", callback_data="pressed"))
    return town_button_chosen.as_markup()

# клавиатура для выбора только с ЗП в сообщениях
async def inline_salary_button() -> InlineKeyboardMarkup:
    salary_button = InlineKeyboardBuilder()
    for item in db.list_of_salary:
        salary_button.add(InlineKeyboardButton(text=db.map_of_salary[item], callback_data=item))
    salary_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="salary_end"))
    return salary_button.adjust(2).as_markup()

# клавиатура для выбранной только с ЗП в сообщениях
async def inline_salary_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    salary_button_chosen = InlineKeyboardBuilder()
    for item in db.list_of_salary:
        if item == chosen:
            salary_button_chosen.add(InlineKeyboardButton(text=db.map_of_salary[item] + "✅", callback_data="pressed"))
        else:
            salary_button_chosen.add(InlineKeyboardButton(text=db.map_of_salary[item], callback_data="pressed"))
    if chosen == "salary_end":
        salary_button_chosen.add(InlineKeyboardButton(text="Завершить поиск✅", callback_data="pressed"))
    return salary_button_chosen.adjust(2).as_markup()

# клавиатура для выбора опыта работы в сообщениях
async def inline_experience_button() -> InlineKeyboardMarkup:
    experience_button = InlineKeyboardBuilder()
    for item in db.list_of_experience:
        experience_button.add(InlineKeyboardButton(text=db.map_of_experience[item], callback_data=item))
    experience_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="exp_end"))
    return experience_button.adjust(2).as_markup()

# клавиатура для выбранного опыта работы в сообщениях
async def inline_experience_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    experience_button_chosen = InlineKeyboardBuilder()
    for item in db.list_of_experience:
        if item == chosen:
            experience_button_chosen.add(InlineKeyboardButton(text=db.map_of_experience[item] + "✅", callback_data="pressed"))
        else:
            experience_button_chosen.add(InlineKeyboardButton(text=db.map_of_experience[item], callback_data="pressed"))
    if chosen == "exp_end":
        experience_button_chosen.add(InlineKeyboardButton(text="Завершить поиск✅", callback_data="pressed"))
    return experience_button_chosen.adjust(2).as_markup()

# клавиатура для выбора графика работы в сообщениях
async def inline_employment_button() -> InlineKeyboardMarkup:
    employment_button = InlineKeyboardBuilder()
    for item in db.list_of_employment:
        employment_button.add(InlineKeyboardButton(text=db.map_of_employment[item], callback_data=item))
    employment_button.add(InlineKeyboardButton(text="Завершить поиск", callback_data="empl_end"))
    return employment_button.adjust(2).as_markup()

# клавиатура для выбранного графика работы в сообщениях
async def inline_employment_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    employment_button_chosen = InlineKeyboardBuilder()
    for item in db.list_of_employment:
        if item == chosen:
            employment_button_chosen.add(InlineKeyboardButton(text=db.map_of_employment[item] + "✅", callback_data="pressed"))
        else:
            employment_button_chosen.add(InlineKeyboardButton(text=db.map_of_employment[item], callback_data="pressed"))
    if chosen == "empl_end":
        employment_button_chosen.add(InlineKeyboardButton(text="Завершить поиск✅", callback_data="pressed"))
    return employment_button_chosen.adjust(2).as_markup()

# клавиатура для выбора текста
async def inline_text() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить поиск", callback_data="text_end")]
    ])

# клавиатура при набранном тексте
async def inline_text_chosen(chosen: str) -> InlineKeyboardMarkup:
    if chosen == "text_end":
        return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Завершить поиск✅", callback_data="pressed")]
    ])
    return InlineKeyboardMarkup(inline_keyboard=[])

# клавиатура для следующей/предыдущей вакансии
async def inline_pages_builder(user_id) -> InlineKeyboardMarkup:
    inline_pages = InlineKeyboardBuilder()
    inline_pages.add(InlineKeyboardButton(text="<=", callback_data=("prev" if (db.users[user_id]["page_now"] != 1) else "pressed")))
    inline_pages.add(InlineKeyboardButton(text=str(db.users[user_id]["page_now"])+"/"+str(db.users[user_id]["total_page"]), callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text="=>", callback_data=("next" if (db.users[user_id]["page_now"] !=db.users[user_id]["total_page"]) else "pressed")))
    inline_pages.add(InlineKeyboardButton(text="Завершить поиск", callback_data="final_end"))
    return inline_pages.adjust(3).as_markup()

# клавиатура для выбранной вакансии
async def inline_pages_builder_chosen(user_id) -> InlineKeyboardMarkup:
    inline_pages = InlineKeyboardBuilder()
    inline_pages.add(InlineKeyboardButton(text="<=", callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text=str(db.users[user_id]["page_now"])+"/"+str(db.users[user_id]["total_page"]), callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text="=>", callback_data="pressed"))
    inline_pages.add(InlineKeyboardButton(text="Завершить поиск✅", callback_data="pressed"))
    return inline_pages.adjust(3).as_markup()