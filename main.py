from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from settings import bot_token
from handlers.main_handler import router as main_handler
from handlers.storage.add_handler import router as add_handler
from handlers.passwords.search_handler import router as search_password_handler
from handlers.passwords.add_handler import router as add_password_handler
from handlers.storage.search_handler import router as search_handler
from asyncio import run


async def main():
    bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)

    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_routers(
        main_handler,
        search_handler,
        add_handler,
        search_password_handler,
        add_password_handler
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())


if __name__ == '__main__':
    run(main())
