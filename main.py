import sqlite3

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram .types import Message
from config import TOKEN

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import logging

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    grade TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(f"Привет! Это бот для сбора заявок. Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer("Какой у тебя класс?")
        await state.set_state(Form.grade)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст (число).")

@dp.message(Form.grade)
async def process_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()
    try:
        conn = sqlite3.connect('school_data.db')
        cur = conn.cursor()
        cur.execute('''
        INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
        (user_data['name'], user_data['age'], user_data['grade']))
        conn.commit()
        conn.close()
        await message.answer("Спасибо! Ваши данные сохранены.")
    except Exception as e:
        await message.answer("Произошла ошибка при сохранении данных.")
        logging.error(f"Ошибка при сохранении данных: {e}")
    finally:
        await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())