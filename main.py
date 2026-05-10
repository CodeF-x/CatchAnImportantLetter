import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import logging
import asyncio
from database.models import init_db
from aiogram import Bot, Dispatcher
from handlers import routers
from services.sheduler import check_emails_job


async def main():
    load_dotenv()
    await init_db()
    token = os.getenv("TG_TOKEN")
    print(f"Пароль загружен")
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_routers(*routers)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_emails_job, 'interval', minutes=2, kwargs={'bot': bot})
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
