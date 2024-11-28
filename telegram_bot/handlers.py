from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext

import telegram_bot.keyboards as kb
from telegram_bot.user_requests import make_req
import database.db as db
import database.dynamic_db as ddb

# создание роутера для связи с диспетчером
router = Router()

# класс запроса пользователя
class Request(StatesGroup):
    town = State()
    salary = State()
    experience = State()
    employment = State()
    sort = State()
    text = State()


# обработчик /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    # добавление пользователя в БД
    await ddb.add_user(id=message.from_user.id, name=message.from_user.username,
                       answer_for_req={}, page_now=0, total_page=0, history_req=[], history_ans=[])
    await message.answer(f"Привет, @{message.from_user.username}!\nЯ помогу тебе найти работу мечты",
                         reply_markup=kb.start_button,
                         resize_keyboard=True)

# обработчик /help
@router.message(Command(commands=["help"]))
async def cmd_help(message: Message) -> None:
    await message.answer(f"Привет, @{message.from_user.username}!\nНапиши /start чтобы пользоваться!")

# Обработка команды начала поиска
@router.message(F.text == "Искать🔎")
async def cmd_town(message: Message, state: FSMContext) -> None:
    await state.set_state(Request.town) # установка состояния для town
    await message.answer("Начнем поиск!",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Укажите город, в которым ищите работу:",
                         reply_markup=await kb.inline_town_button())

# Обработка ручного ввода города и запрос на salary
@router.message(Request.town)
async def cmd_salary(message: Message, state: FSMContext) -> None:
    # проверка на нахождение введенного города в списке HH
    if message not in db.map_of_towns.values():
        await message.answer("К сожалению, пока этот город недоступен\nНапишите, пожалуйста, другой")
    else:
        await state.update_data(town=message.text) # запись в поле town
        await state.set_state(Request.salary) # установка состояния для salary
        await message.answer("Показывать вакансии только с ЗП:",
                             reply_markup=await kb.inline_salary_button())

# Обработка выбора города кроме другого и запрос на salary
@router.callback_query(F.data.in_(db.list_of_towns[:-1]))
async def cmd_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(town=(await ddb.get_town(callback.data)).tg_int) # запись данных в поле town
    await state.set_state(Request.salary) # установка состояния для salary
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Показывать вакансии только с ЗП:",
                                  reply_markup=await kb.inline_salary_button())

# Обработка выбора другого города
@router.callback_query(F.data == "other")
async def cmd_other_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.town) # установка состояние для town
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Напишите ваш город:")

# Обработка выбора salary и запрос на experience
@router.callback_query(F.data.in_(db.list_of_salary))
async def cmd_salary_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(salary=(await ddb.get_salary(callback.data)).tg_int) # запись данных в поле salary
    await state.set_state(Request.experience) # установка состояния для experience
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_salary_button_chosen(callback.data))
    await callback.message.answer("Укажите опыт работы:",
                                  reply_markup=await kb.inline_experience_button())

# Обработка выбора experience и запрос на employment
@router.callback_query(F.data.in_(db.list_of_experience))
async def cmd_exp_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(experience=(await ddb.get_experience(callback.data)).tg_int) # запись данных в поле experience
    await state.set_state(Request.employment) # установка состояния для employment
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_experience_button_chosen(callback.data))
    await callback.message.answer("Укажите график работы:",
                                  reply_markup=await kb.inline_employment_button())

# Обработка выбора employment и запрос на sort
@router.callback_query(F.data.in_(db.list_of_employment))
async def cmd_empl_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(employment=(await ddb.get_employment(callback.data)).tg_int) # запись данных в поле employment
    await state.set_state(Request.sort) # установка состояния для sort
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_employment_button_chosen(callback.data))
    await callback.message.answer("Сортировать по:",
                                  reply_markup=await kb.inline_sort_button())

# # Обработка выбора sort и запрос на text
@router.callback_query(F.data.in_(db.list_of_sort))
async def cmd_sort_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(sort=(await ddb.get_sort(callback.data)).tg_int) # запись данных в поле sort
    await state.set_state(Request.text) # установка состояния для text
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_sort_button_chosen(callback.data))
    await callback.message.answer("Напишите описание вакансии:")

# обработка описания вакансии и запрос в парсер
@router.message(Request.text)
async def cmd_text(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id # получение ID пользователя
    await state.update_data(text=message.text) # запись данных в поле text
    data = await state.get_data() # запрос данных из Requests
    await state.clear() # очистка состояния
    await message.answer("Поиск•••")
    data_from_parser = await make_req(data) # запрос в парсер
    page_now = 1 # текущая страница
    total_page = len(data_from_parser) # всего страниц
    await ddb.update_user(user_id, {"answer_for_req" : data_from_parser, "page_now" : page_now, "total_page" : total_page}) # обновление данных в БД
    if total_page == 0:
        text = "Подходящих вакансий не найдено"
        await message.answer(text,
                             reply_markup=kb.start_button,
                             resize_keyboard=True)
    else:
        text = (f"✔ {data_from_parser[0]["title"]}\n✔ {data_from_parser[0]["employer"]}\n"
                f"✔ {data_from_parser[0]["salary_info"]}\n✔ {data_from_parser[0]["url"]}")

        await message.answer(text,
                             reply_markup=await kb.inline_pages_builder(user_id))

# обработка запроса на следующую страницу в просмотре вакансий
@router.callback_query(F.data == "next")
async def cmd_next(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id  # получение ID пользователя
    data = await ddb.get_user(user_id) # получение данных из БД
    await ddb.update_user(user_id, {"page_now" : (data.page_now + 1)}) # запись данных в БД
    text = (f"✔ {data.answer_for_req[data.page_now]["title"]}\n"
            f"✔ {data.answer_for_req[data.page_now]["employer"]}\n"
            f"✔ {data.answer_for_req[data.page_now]["salary_info"]}\n"
            f"✔ {data.answer_for_req[data.page_now]["url"]}")
    await callback.message.edit_text(text,
                                     reply_markup=await kb.inline_pages_builder(user_id))

# обработка запроса на предыдущую страницу в просмотре вакансий
@router.callback_query(F.data == "prev")
async def cmd_prev(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id # получение ID пользователя
    data = await ddb.get_user(user_id)  # получение данных из БД
    await ddb.update_user(user_id, {"page_now" : (data.page_now - 1)}) # запись данных в БД
    text = (f"✔ {data.answer_for_req[data.page_now - 2]["title"]}\n"
            f"✔ {data.answer_for_req[data.page_now - 2]["employer"]}\n"
            f"✔ {data.answer_for_req[data.page_now - 2]["salary_info"]}\n"
            f"✔ {data.answer_for_req[data.page_now - 2]["url"]}")
    await callback.message.edit_text(text,
                                     reply_markup=await kb.inline_pages_builder(user_id))

# обработка завершить запрос в town
@router.callback_query(F.data == "town_end")
async def cmd_town_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка завершить запрос в salary
@router.callback_query(F.data == "salary_end")
async def cmd_salary_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_salary_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка завершить запрос в experience
@router.callback_query(F.data == "exp_end")
async def cmd_exp_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_experience_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка завершить запрос в employment
@router.callback_query(F.data == "empl_end")
async def cmd_empl_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear() # очистка состояния
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_employment_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка завершить запрос в sort
@router.callback_query(F.data == "sort_end")
async def cmd_sort_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear() # очистка состояния
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_sort_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка завершить запрос при просмотре вакансий
@router.callback_query(F.data == "final_end")
async def cmd_final_end(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    await state.clear() # очистка состояния
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_pages_builder_chosen(user_id))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка шага назад от запроса salary
@router.callback_query(F.data == "salary_back")
async def cmd_salary_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.town)
    await callback.message.delete()

# обработка шага назад от запроса experience
@router.callback_query(F.data == "exp_back")
async def cmd_exp_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.salary)
    await callback.message.delete()

# обработка шага назад от запроса employment
@router.callback_query(F.data == "empl_back")
async def cmd_empl_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.experience)
    await callback.message.delete()

# обработка шага назад от запроса sort
@router.callback_query(F.data == "sort_back")
async def cmd_sort_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.employment)
    await callback.message.delete()
