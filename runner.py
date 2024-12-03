import logging
import os
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
import asyncio

from telegram_bot.handlers import router

# получение данных из dotenv
load_dotenv()

# инициализация подключения бота
bot = Bot(token=os.getenv("TG_TOKEN"))

# интерфейс управления
disp = Dispatcher()

# функция запуска
async def main() -> None:
    disp.include_router(router)
    await disp.start_polling(bot)

if __name__ == "__main__":
    # вывод в терминал действий бота, выключить в проде!!!
    logging.basicConfig(level=logging.INFO)

    # запуск бота
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Finished with errors")
    finally:
        print("EXIT")
