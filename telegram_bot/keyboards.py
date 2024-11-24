from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from database.db import *

# клавиатура для кнопки поиска в клавиатуре
start_button = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Искать🔎")]
])

# клавиатура для выбора города в сообщениях
async def inline_town_button() -> InlineKeyboardMarkup:
    town_button = InlineKeyboardBuilder()
    for item in list_of_towns:
        town_button.add(InlineKeyboardButton(text=map_of_towns[item], callback_data=item))
    return town_button.adjust(2).as_markup()

# клавиатура для написанного города в сообщениях
async def inline_town_button_texted() -> InlineKeyboardMarkup:
    town_button = InlineKeyboardBuilder()
    for item in list_of_towns:
        town_button.add(InlineKeyboardButton(text=map_of_towns[item], callback_data="pressed"))
    return town_button.adjust(2).as_markup()

# клавиатура для выбранного города в сообщениях
async def inline_town_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    town_button_chosen = InlineKeyboardBuilder()
    for item in list_of_towns:
        if item == chosen:
            town_button_chosen.add(InlineKeyboardButton(text=map_of_towns[item]+"✅", callback_data="pressed"))
        else:
            town_button_chosen.add(InlineKeyboardButton(text=map_of_towns[item], callback_data="pressed"))
    return town_button_chosen.adjust(2).as_markup()


# клавиатура для выбора только с ЗП в сообщениях
async def inline_salary_button() -> InlineKeyboardMarkup:
    salary_button = InlineKeyboardBuilder()
    for item in list_of_salary:
        salary_button.add(InlineKeyboardButton(text=map_of_salary[item], callback_data=item))
    return salary_button.adjust(2).as_markup()

# клавиатура для выбранной только с ЗП в сообщениях
async def inline_salary_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    salary_button_chosen = InlineKeyboardBuilder()
    for item in list_of_salary:
        if item == chosen:
            salary_button_chosen.add(InlineKeyboardButton(text=map_of_salary[item] + "✅", callback_data="pressed"))
        else:
            salary_button_chosen.add(InlineKeyboardButton(text=map_of_salary[item], callback_data="pressed"))
    return salary_button_chosen.adjust(2).as_markup()

# клавиатура для выбора опыта работы в сообщениях
async def inline_experience_button() -> InlineKeyboardMarkup:
    experience_button = InlineKeyboardBuilder()
    for item in list_of_experience:
        experience_button.add(InlineKeyboardButton(text=map_of_experience[item], callback_data=item))
    return experience_button.adjust(2).as_markup()

# клавиатура для выбранного опыта работы в сообщениях
async def inline_experience_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    experience_button_chosen = InlineKeyboardBuilder()
    for item in list_of_experience:
        if item == chosen:
            experience_button_chosen.add(InlineKeyboardButton(text=map_of_experience[item] + "✅", callback_data="pressed"))
        else:
            experience_button_chosen.add(InlineKeyboardButton(text=map_of_experience[item], callback_data="pressed"))
    return experience_button_chosen.adjust(2).as_markup()

# клавиатура для выбора графика работы в сообщениях
async def inline_employment_button() -> InlineKeyboardMarkup:
    employment_button = InlineKeyboardBuilder()
    for item in list_of_employment:
        employment_button.add(InlineKeyboardButton(text=map_of_employment[item], callback_data=item))
    return employment_button.adjust(2).as_markup()

# клавиатура для выбранного графика работы в сообщениях
async def inline_employment_button_chosen(chosen: str) -> InlineKeyboardMarkup:
    employment_button_chosen = InlineKeyboardBuilder()
    for item in list_of_employment:
        if item == chosen:
            employment_button_chosen.add(InlineKeyboardButton(text=map_of_employment[item] + "✅", callback_data="pressed"))
        else:
            employment_button_chosen.add(InlineKeyboardButton(text=map_of_employment[item], callback_data="pressed"))
    return employment_button_chosen.adjust(2).as_markup()