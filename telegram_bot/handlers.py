from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import json

import telegram_bot.keyboards as kb
from telegram_bot.user_requests import make_req
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
async def cmd_start(message: Message) -> None:
    # добавление пользователя в БД
    await ddb.add_user(user_id=message.from_user.id,
                       vac_now=0, vac_total=0, page=0, history_req=[], history_ans=[])
    await message.answer(f"Привет!\nЯ помогу тебе найти работу мечты",
                         reply_markup=kb.start_button,
                         resize_keyboard=True)

# обработчик /help
@router.message(Command(commands=["help"]))
async def cmd_help(message: Message) -> None:
    await message.answer(f"Привет!\nНапиши /start чтобы пользоваться!")

# Обработка команды начала поиска
@router.message(F.text == "Искать🔎")
async def cmd_town(message: Message, state: FSMContext) -> None:
    await state.set_state(Request.town) # установка состояния для town
    await ddb.update_user(message.from_user.id, {"page" : 0})
    await message.answer("Начнем поиск!",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Укажите город, в которым ищите работу:",
                         reply_markup=await kb.inline_town_button())

# Обработка ручного ввода города и запрос на salary
@router.message(Request.town)
async def cmd_salary(message: Message, state: FSMContext) -> None:
    # проверка на нахождение введенного города в списке HH
    if message.text not in (await ddb.get_column("cities", "city_name")):
        await message.answer("К сожалению, пока этот город недоступен\nНапишите, пожалуйста, другой")
    else:
        await state.update_data(town=message.text) # запись в поле town
        await state.set_state(Request.salary) # установка состояния для salary
        await message.answer("Показывать вакансии только с ЗП:",
                             reply_markup=await kb.inline_salary_button())

# Обработка выбора города кроме другого и запрос на salary
@router.callback_query(F.data.in_(["Moscow", "Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan", "Nizhny"]))
async def cmd_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(town=(await ddb.get_town(callback.data, "key")).value) # запись данных в поле town
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
@router.callback_query(F.data.in_(["True", "False"]))
async def cmd_salary_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(salary=(await ddb.get_salary(callback.data, "key")).value) # запись данных в поле salary
    await state.set_state(Request.experience) # установка состояния для experience
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_salary_button_chosen(callback.data))
    await callback.message.answer("Укажите опыт работы:",
                                  reply_markup=await kb.inline_experience_button())

# Обработка выбора experience и запрос на employment
@router.callback_query(F.data.in_(["noExperience", "between1And3", "between3And6", "moreThan6"]))
async def cmd_exp_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(experience=(await ddb.get_experience(callback.data, "key")).value) # запись данных в поле experience
    await state.set_state(Request.employment) # установка состояния для employment
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_experience_button_chosen(callback.data))
    await callback.message.answer("Укажите график работы:",
                                  reply_markup=await kb.inline_employment_button())

# Обработка выбора employment и запрос на sort
@router.callback_query(F.data.in_(["full", "part", "project", "probation"]))
async def cmd_empl_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(employment=(await ddb.get_employment(callback.data, "key")).value) # запись данных в поле employment
    await state.set_state(Request.sort) # установка состояния для sort
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_employment_button_chosen(callback.data))
    await callback.message.answer("Сортировать по:",
                                  reply_markup=await kb.inline_sort_button())

# # Обработка выбора sort и запрос на text
@router.callback_query(F.data.in_(["relevance", "publication_time", "salary_desc", "salary_asc"]))
async def cmd_sort_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(sort=(await ddb.get_sort(callback.data, "key")).value) # запись данных в поле sort
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
    data_from_parser = await make_req(data, 0) # запрос в парсер
    vac_total = len(data_from_parser) # всего вакансий на странице
    vac_now = min(vac_total, 1) # текущая вакансия
    txt = ""
    for item in data_from_parser:
        txt += json.dumps(item, ensure_ascii=False) + "#"
    await ddb.update_user(user_id, {"vac_now" : vac_now, "vac_total" : vac_total,
                                             "history_req" : [json.dumps(data, ensure_ascii=False)],
                                             "history_ans" : [txt]}) # обновление данных в БД
    if vac_total == 0:
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
    await ddb.update_user(user_id, {"vac_now" : (data.vac_now + 1)}) # запись данных в БД
    text = (f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now])["title"]}\n"
            f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now])["employer"]}\n"
            f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now])["salary_info"]}\n"
            f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now])["url"]}")
    await callback.message.edit_text(text,
                                     reply_markup=await kb.inline_pages_builder(user_id))

# обработка запроса на предыдущую страницу в просмотре вакансий
@router.callback_query(F.data == "prev")
async def cmd_prev(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id # получение ID пользователя
    data = await ddb.get_user(user_id)  # получение данных из БД
    await ddb.update_user(user_id, {"vac_now" : (data.vac_now - 1)}) # запись данных в БД
    text = (f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now - 2])["title"]}\n"
            f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now - 2])["employer"]}\n"
            f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now - 2])["salary_info"]}\n"
            f"✔ {json.loads(data.history_ans[-1].split("#")[data.vac_now - 2])["url"]}")
    await callback.message.edit_text(text,
                                     reply_markup=await kb.inline_pages_builder(user_id))

# обработка варианте ещё при выводе вакансий
@router.callback_query(F.data == "morevac")
async def cmd_more(callback: CallbackQuery):
    data = await ddb.get_user(callback.from_user.id)
    if data.vac_total < 50:
        await callback.answer(text="Вакансий больше нет", show_alert=True)
    else:
        request_to_parser = json.loads(data.history_req[-1])
        data_from_parser = await make_req(request_to_parser, data.page + 1)  # запрос в парсер
        vac_total = len(data_from_parser)
        vac_now = min(vac_total, 1)
        txt = ""
        for item in data_from_parser:
            txt += json.dumps(item, ensure_ascii=False) + "#"
        await ddb.update_user(callback.from_user.id, {"vac_now": vac_now, "vac_total": vac_total, "page": data.page + 1,
                                                               "history_req" : [json.dumps(request_to_parser, ensure_ascii=False)],
                                                               "history_ans" : [txt]})
        if vac_total == 0:
            await callback.message.edit_reply_markup(reply_markup=await kb.inline_pages_builder_chosen(callback.from_user.id))
            await callback.message.answer(text="Подходящих вакансий не найдено",
                                          reply_markup=kb.start_button,
                                          resize_keyboard=True)
        else:
            text = (f"✔ {data_from_parser[0]["title"]}\n✔ {data_from_parser[0]["employer"]}\n"
                    f"✔ {data_from_parser[0]["salary_info"]}\n✔ {data_from_parser[0]["url"]}")

            await callback.message.edit_text(text,
                                             reply_markup=await kb.inline_pages_builder(callback.from_user.id))



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