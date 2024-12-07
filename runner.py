from telegram_bot.handlers import router, send_daily_message

import logging
import os
import asyncio
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# получение данных из dotenv
load_dotenv()

# интерфейс управления
disp = Dispatcher()

# функция запуска
async def main() -> None:
    async with Bot(token=os.getenv("TG_TOKEN")) as bot:
        # Планировщик ежедневных сообщений
        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_daily_message, 'cron', hour=19, minute=0, args=[bot])
        scheduler.start()

        # Запуск бота
        disp.include_router(router)
        await disp.start_polling(bot)

# запуск с обработкой ошибок
if __name__ == "__main__":
    # вывод в терминал действий бота, выключить в проде!!!
    logging.basicConfig(level=logging.INFO)

    # запуск бота
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        logging.info("EXIT")
