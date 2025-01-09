import asyncio
import bot_config
import database
import handlers

async def main():
    # Запускаем создание таблицы базы данных
    await database.create_table()
    await bot_config.dp.start_polling(bot_config.bot)

if __name__ == "__main__":
    asyncio.run(main())
