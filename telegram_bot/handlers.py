from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup,State
from aiogram.fsm.context import FSMContext
import keyboards as kb
from user_requests import make_req
import database.db as db

# создание роутера для связи с диспетчером
router = Router()

first_button = 0

# класс запроса пользователя
class Request(StatesGroup):
    search = State()
    town = State()
    salary = State()
    experience = State()
    employment = State()
    text = State()

# обработчик /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    db.users[message.from_user.id] = {
        "answer_for_req" : {},
        "page_now" : 0,
        "total_page" : 0
    }

    await state.set_state(Request.search)
    await message.answer(f"Привет, @{message.from_user.username}!\nЯ помогу тебе найти работу мечты",
                         reply_markup=kb.start_button,
                         resize_keyboard=True)

# обработчик /help
@router.message(Command(commands=["help"]))
async def cmd_help(message: Message) -> None:
    await message.answer(f"Привет, @{message.from_user.username}!\nНапиши /start чтобы пользоваться!")

# запрос на город
@router.message(Request.search)
async def cmd_town(message: Message, state: FSMContext) -> None:
    await state.set_state(Request.town)
    await message.answer("Начнем поиск!",
                         reply_markup=ReplyKeyboardRemove())
    inl_button = await message.answer("Укажите город, в которым ищите работу:",
                         reply_markup=await kb.inline_town_button())
    first_button = inl_button.message_id

# запись города и запрос на только с ЗП
@router.message(Request.town)
async def cmd_salary(message: Message, state: FSMContext) -> None:
    if message.text not in db.map_of_towns.values():
        await message.answer("К сожалению, пока этот город недоступен\nНапишите, пожалуйста, другой")
    else:
        await state.update_data(town=message.text)
        await state.set_state(Request.salary)
        await message.answer("Показывать вакансии только с ЗП:",
                             reply_markup=await kb.inline_salary_button())

# обработка вариантов ответа в кнопке town_button
@router.callback_query(F.data.in_(db.list_of_towns[:-1]))
async def cmd_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(town=db.map_of_towns[callback.data])
    await state.set_state(Request.salary)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Показывать вакансии только с ЗП:",
                                  reply_markup=await kb.inline_salary_button())

# обработка варианта другой город
@router.callback_query(F.data == "other")
async def cmd_other_town_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.town)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Напишите ваш город:")

# обработка вариантов ответа в кнопке salary_button
@router.callback_query(F.data.in_(db.list_of_salary))
async def cmd_salary_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(salary=db.map_of_salary[callback.data])
    await state.set_state(Request.experience)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_salary_button_chosen(callback.data))
    await callback.message.answer("Укажите опыт работы:",
                                  reply_markup=await kb.inline_experience_button())

# обработка вариантов ответа в кнопке experience_button
@router.callback_query(F.data.in_(db.list_of_experience))
async def cmd_exp_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(experience=db.map_of_experience[callback.data])
    await state.set_state(Request.employment)
    await callback.message.edit_reply_markup(
        reply_markup=await kb.inline_experience_button_chosen(callback.data))
    await callback.message.answer("Укажите график работы:",
                                  reply_markup=await kb.inline_employment_button())

# обработка вариантов ответа в кнопке employment_button
@router.callback_query(F.data.in_(db.list_of_employment))
async def cmd_empl_button(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(employment=db.map_of_employment[callback.data])
    await state.set_state(Request.text)
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_employment_button_chosen(callback.data))
    await callback.message.answer("Напишите описание вакансии:")

# обработка описания вакансии
@router.message(Request.text)
async def cmd_text(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    await state.update_data(text=message.text)
    data = await state.get_data()
    await state.clear()
    await message.answer("Поиск•••")
    db.users[user_id]["answer_for_req"] = await make_req(data)
    db.users[user_id]["page_now"] = 1
    db.users[user_id]["total_page"] = len(db.users[user_id]["answer_for_req"])
    if db.users[user_id]["total_page"] == 0:
        await state.set_state(Request.search)
        text = "Подходящих вакансий не найдено"
        await message.answer(text,
                             reply_markup=kb.start_button,
                             resize_keyboard=True)
    else:
        text = (f"✔ {db.users[user_id]["answer_for_req"][0]["title"]}\n✔ {db.users[user_id]["answer_for_req"][0]["employer"]}\n"
                f"✔ {db.users[user_id]["answer_for_req"][0]["salary_info"]}\n✔ {db.users[user_id]["answer_for_req"][0]["url"]}")

        await message.answer(text,
                             reply_markup=await kb.inline_pages_builder(user_id))

# обработка запроса на следующую страницу
@router.callback_query(F.data == "next")
async def cmd_next(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    db.users[user_id]["page_now"] += 1
    text = (f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["title"]}\n"
            f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["employer"]}\n"
            f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["salary_info"]}\n"
            f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["url"]}")
    await callback.message.edit_text(text,
                                     reply_markup=await kb.inline_pages_builder(user_id))

# обработка запроса на предыдущую страницу
@router.callback_query(F.data == "prev")
async def cmd_prev(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    db.users[user_id]["page_now"] -= 1
    text = (f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["title"]}\n"
            f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["employer"]}\n"
            f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["salary_info"]}\n"
            f"✔ {db.users[user_id]["answer_for_req"][db.users[user_id]["page_now"] - 1]["url"]}")
    await callback.message.edit_text(text,
                                     reply_markup=await kb.inline_pages_builder(user_id))

# обработка преждевременного конца запроса town
@router.callback_query(F.data == "town_end")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Request.search)
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_town_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка преждевременного конца запроса salary
@router.callback_query(F.data == "salary_end")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Request.search)
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_salary_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка преждевременного конца запроса experience
@router.callback_query(F.data == "exp_end")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Request.search)
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_experience_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка преждевременного конца запроса employment
@router.callback_query(F.data == "empl_end")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Request.search)
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_employment_button_chosen(callback.data))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка конца запроса вакансий
@router.callback_query(F.data == "final_end")
async def cmd_final_end(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    await state.clear()
    await state.set_state(Request.search)
    await callback.message.edit_reply_markup(reply_markup=await kb.inline_pages_builder_chosen(user_id))
    await callback.message.answer("Поиск завершен!",
                                  reply_markup=kb.start_button)

# обработка шага назад от запроса salary
@router.callback_query(F.data == "salary_back")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    #await callback.bot.edit_message_reply_markup(chat_id=callback.message.chat.id,
    #                                    message_id=first_button,
    #                                    reply_markup=None)
    await state.set_state(Request.town)
    await callback.message.delete()

# обработка шага назад от запроса experience
@router.callback_query(F.data == "exp_back")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.salary)
    await callback.message.delete()

# обработка шага назад от запроса employment
@router.callback_query(F.data == "empl_back")
async def cmd_end(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Request.experience)
    await callback.message.delete()