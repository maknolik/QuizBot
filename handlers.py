from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
import bot_config
import database
import quiz_data

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for index, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{index}"
        ))

    builder.adjust(1)
    return builder.as_markup()

@bot_config.dp.callback_query(F.data.startswith("answer_"))
async def answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await database.get_quiz_index(callback.from_user.id)
    selected_option_index = int(callback.data.split('_')[1])
    correct_option_index = quiz_data.quiz_data[current_question_index]['correct_option']
    user_response = quiz_data.quiz_data[current_question_index]['options'][selected_option_index]

    if selected_option_index == correct_option_index:
        await callback.message.answer(f"Верно! Ваш ответ: {user_response}")
        result = await database.get_quiz_result(callback.from_user.id)
        correct_answers = result['correct_answers']
        correct_answers += 1
        await database.save_quiz_result(callback.from_user.id, correct_answers, len(quiz_data.quiz_data))
    else:
        await callback.message.answer(f"Неправильно. Ваш ответ: {user_response}. Правильный ответ: {quiz_data.quiz_data[current_question_index]['options'][correct_option_index]}")

    current_question_index += 1
    await database.update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data.quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        result = await database.get_quiz_result(callback.from_user.id)
        correct_answers = result['correct_answers']
        total_questions = len(quiz_data.quiz_data)
        await database.save_quiz_result(callback.from_user.id, correct_answers, total_questions)
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {correct_answers}/{total_questions}", reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Посмотреть статистику всех попыток")],
                [types.KeyboardButton(text="Пройти квиз снова")]
            ],
            resize_keyboard=True
        ))

# Хэндлер на команду /start
@bot_config.dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await database.get_quiz_index(user_id)
    correct_index = quiz_data.quiz_data[current_question_index]['correct_option']
    opts = quiz_data.quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data.quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await database.update_quiz_index(user_id, current_question_index)
    await database.save_quiz_result(user_id, 0, len(quiz_data.quiz_data))
    await get_question(message, user_id)

# Хэндлер на команду /quiz
@bot_config.dp.message(F.text=="Начать игру")
@bot_config.dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await database.save_quiz_result(message.from_user.id, 0, len(quiz_data.quiz_data))
    await new_quiz(message)

# Хэндлер на команду /stats
@bot_config.dp.message(F.text=="Посмотреть статистику всех попыток")
async def cmd_stats(message: types.Message):
    results = await database.get_all_quiz_results()
    stats_message = "Статистика всех попыток:\n"
    for user_id, result in results.items():
        stats_message += f"Пользователь {user_id}: {result['correct_answers']}/{result['total_questions']}\n"
    await message.answer(stats_message)
