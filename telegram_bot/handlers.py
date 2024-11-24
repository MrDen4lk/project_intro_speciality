from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import keyboards as kb
import user_requests
from database.db import *

# создание роутера для связи с диспетчером
router = Router()

# класс запроса пользователя
class Request(StatesGroup):
    town = State()
    salary = State()
    experience = State()
    employment = State()
    text = State()

# обработчик /start
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(f"Привет, @{message.from_user.username}!\nЯ помогу тебе найти работу мечты",
                         reply_markup=kb.start_button,
                         resize_keyboard=True)

# запрос на город
@router.message(F.text == "Искать🔎")
async def cmd_town(message: Message, state: FSMContext) -> None:
    await message.answer("Начнем поиск!",
                         reply_markup=ReplyKeyboardRemove())
    await message.answer("Укажите город, в которым ищите работу:",
                         reply_markup=await kb.inline_town_button(),
                         resize_keyboard=True)

# запись города и запрос на только с ЗП
@router.message(Request.town)
async def cmd_salary(message: Message, state: FSMContext) -> None:
    await state.update_data(town=message.text)
    await state.set_state(Request.salary)
    await message.answer("Показывать вакансии только с ЗП:",
                         reply_markup=await kb.inline_salary_button(),
                         resize_keyboard=True)

# обработка вариантов ответа в кнопке town_button
@router.callback_query(F.data.in_(kb.list_of_towns[:-1]))
async def cmd_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(town=map_of_towns[callback.data])
    await state.set_state(Request.salary)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Показывать вакансии только с ЗП:",
                         reply_markup=await kb.inline_salary_button(),
                         resize_keyboard=True)

# обработка варианта другой город
@router.callback_query(F.data == "other")
async def cmd_other_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.town)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Напишите ваш город:")

# обработка вариантов ответа в кнопке salary_button
@router.callback_query(F.data.in_(kb.list_of_salary))
async def cmd_salary_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(salary=map_of_salary[callback.data])
    await state.set_state(Request.experience)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_salary_button_chosen(callback.data))
    await callback.message.answer("Укажите опыт работы:",
                         reply_markup=await kb.inline_experience_button(),
                         resize_keyboard=True)

# обработка вариантов ответа в кнопке experience_button
@router.callback_query(F.data.in_(kb.list_of_experience))
async def cmd_exp_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(experience=map_of_experience[callback.data])
    await state.set_state(Request.employment)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_experience_button_chosen(callback.data))
    await callback.message.answer("Укажите график работы:",
                         reply_markup=await kb.inline_employment_button(),
                         resize_keyboard=True)

# обработка вариантов ответа в кнопке employment_button
@router.callback_query(F.data.in_(kb.list_of_employment))
async def cmd_empl_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(employment=map_of_employment[callback.data])
    await state.set_state(Request.text)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_employment_button_chosen(callback.data))
    await callback.message.answer("Напишите описание вакансии:")

# обработка описания вакансии
@router.message(Request.text)
async def cmd_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    data = await state.get_data()
    await message.answer("Предложенные вакансии: ",
                                  reply_markup=kb.start_button,
                                  resize_keyboard=True)
    await state.clear()
    answer = await user_requests.make_req(data)
    await message.answer(answer[0])