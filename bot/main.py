# bot/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # 👈 Добавить импорт

from settings.config import config
from infrastructure.database.accessor import check_connection, close_engine
from bot.presentation.handlers import start, catalog, buy, admin


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Проверка подключения к БД
    if not await check_connection():
        logging.error("❌ Не удалось подключиться к базе данных")
        return
    
    # Создаем бота (новый синтаксис)
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # 👈 Новый способ
    )
    dp = Dispatcher()
    
    # Подключаем роутеры
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(buy.router)
    dp.include_router(admin.router)
    
    logging.info("✅ Бот запущен!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await close_engine()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())