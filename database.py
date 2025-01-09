import aiosqlite

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'

async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (user_id INTEGER PRIMARY KEY, correct_answers INTEGER, total_questions INTEGER)''')
        # Сохраняем изменения
        await db.commit()

async def save_quiz_result(user_id, correct_answers, total_questions):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_results (user_id, correct_answers, total_questions) VALUES (?, ?, ?)', (user_id, correct_answers, total_questions))
        await db.commit()

async def get_quiz_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT correct_answers, total_questions FROM quiz_results WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                return {"correct_answers": result[0], "total_questions": result[1]}
            else:
                return {"correct_answers": 0, "total_questions": 0}

async def get_all_quiz_results():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, correct_answers, total_questions FROM quiz_results') as cursor:
            results = await cursor.fetchall()
            return {user_id: {'correct_answers': correct_answers, 'total_questions': total_questions} for user_id, correct_answers, total_questions in results}
