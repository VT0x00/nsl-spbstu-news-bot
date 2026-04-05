import dotenv
import asyncio
from aiogram import Bot, Router, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import modules.make_message


env_file = "./.env"

TELEGRAM_API_TOKEN = dotenv.get_key(env_file, 'TELEGRAM_API_TOKEN')
ADMIN_ID = dotenv.get_key(env_file, 'ADMIN_ID')
CHANNEL_ID = dotenv.get_key(env_file, 'CHANNEL_ID')

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_API_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message):
    await bot.send_message(message.chat.id, "Данный бот предназначен для публикации новостей ЕНЛ СПбПУ в канал <a href='https://t.me/nslspbstu'>Новости ЕНЛ СПбПУ</a>")


@start_router.message()
async def unknown(message: Message):
    await bot.send_message(message.chat.id, "Команда не распознана")


async def send_news():
    try:
        site_msgs, err = modules.make_message.mk_msg_site()
        if err == "Обновлений нет":
            print(err)
            pass
        elif err != None:
            print(err)
            await bot.send_message(ADMIN_ID, err)
        else:
            for site_msg in site_msgs:
                await bot.send_message(CHANNEL_ID, site_msg)
                await asyncio.sleep(10)
                print(site_msg)
    except Exception as err:
        await bot.send_message(ADMIN_ID, f"Аn error occurred:\n```\n{err}\n```")
        print(f"{CHANNEL_ID=}")


async def send_news_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_news, 'interval', seconds=60*10) # TODO: CHANGE 60*10 to 60*60
    scheduler.start()


async def main():
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(send_news_scheduler())

        dp.include_router(start_router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as err:
        await bot.send_message(ADMIN_ID, f"Аn error occurred:\n```\n{err}\n```")
        print(f"ERROR MAIN: {err=}")
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
