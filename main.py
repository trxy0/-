import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

API_TOKEN = '7343562026:AAHx983iRuX0dEVtMa5abowpAF3gI39UgbM'

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Пример рецептов
recipes = [
    {"name": "Овсянка с фруктами", "calories": 320, "b": 8, "j": 5, "u": 55, "type": "завтрак"},
    {"name": "Куриная грудка с овощами", "calories": 400, "b": 35, "j": 10, "u": 20, "type": "обед"},
    {"name": "Салат с тунцом", "calories": 280, "b": 22, "j": 12, "u": 10, "type": "ужин"},
    {"name": "Паста с томатами", "calories": 450, "b": 12, "j": 15, "u": 60, "type": "обед"},
    {"name": "Омлет с сыром и зеленью", "calories": 350, "b": 20, "j": 25, "u": 5, "type": "завтрак"},
    {"name": "Йогуртовый десерт с ягодами", "calories": 250, "b": 10, "j": 8, "u": 35, "type": "десерт"},
]

user_goals = {}

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽 Поиск по предпочтениям")],
        [KeyboardButton(text="🔥 Поиск по калориям")],
        [KeyboardButton(text="📅 Рацион на день")],
        [KeyboardButton(text="📊 Показать БЖУ")],
        [KeyboardButton(text="🎯 Установить цель по калориям")],
        [KeyboardButton(text="❌ Отменить")]
    ],
    resize_keyboard=True
)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я бот \"Рецепты на каждый день\". Выбери, что ты хочешь:", reply_markup=main_kb)

@dp.message(F.text == "🍽 Поиск по предпочтениям")
async def preference_search(message: types.Message):
    types_set = sorted(set(r['type'] for r in recipes))
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t)] for t in types_set] + [[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )
    await message.answer("Выберите категорию:", reply_markup=kb)

@dp.message(F.text.in_({"завтрак", "обед", "ужин", "десерт"}))
async def preference_result(message: types.Message):
    selected_type = message.text.lower()
    filtered = [r for r in recipes if r['type'] == selected_type]
    if filtered:
        text = f"Вот рецепты категории '{selected_type}':\n" + "\n".join(f"{r['name']} – {r['calories']} ккал" for r in filtered)
    else:
        text = f"Нет рецептов в категории '{selected_type}'"
    await message.answer(text, reply_markup=main_kb)

@dp.message(F.text == "🔙 Назад")
async def back_to_menu(message: types.Message):
    await message.answer("Возвращаюсь в главное меню.", reply_markup=main_kb)

@dp.message(F.text == "🔥 Поиск по калориям")
async def calories_search(message: types.Message):
    await message.answer("Введите желаемое количество калорий (например: 400):")

@dp.message(F.text.regexp(r"^\d+$"))
async def show_by_calories(message: types.Message):
    cal = int(message.text)
    filtered = [r for r in recipes if r["calories"] <= cal]
    if not filtered:
        await message.answer("Нет блюд с такой калорийностью")
    else:
        result = "Вот подходящие рецепты:\n" + "\n".join(f"{r['name']} – {r['calories']} ккал" for r in filtered)
        await message.answer(result)

@dp.message(F.text == "📅 Рацион на день")
async def day_plan(message: types.Message):
    user_id = message.from_user.id
    goal = user_goals.get(user_id, 1800)
    total = 0
    plan = []
    for r in recipes:
        if total + r['calories'] <= goal:
            plan.append(r)
            total += r['calories']
    result = f"Рацион на день (цель: {goal} ккал):\n" + "\n".join(f"{r['name']} – {r['calories']} ккал" for r in plan) + f"\nИтого: {total} ккал"
    await message.answer(result)

@dp.message(F.text == "📊 Показать БЖУ")
async def show_bju(message: types.Message):
    text = "БЖУ по рецептам:\n"
    for r in recipes:
        text += f"{r['name']}: Б {r['b']}г / Ж {r['j']}г / У {r['u']}г\n"
    await message.answer(text)

@dp.message(F.text == "🎯 Установить цель по калориям")
async def set_goal_prompt(message: types.Message):
    await message.answer("Введите вашу дневную цель по калориям (например: 2000):")

@dp.message(F.text.regexp(r"^\d{4}$"))
async def set_goal_value(message: types.Message):
    cal = int(message.text)
    if 1000 <= cal <= 4000:
        user_goals[message.from_user.id] = cal
        await message.answer(f"Цель установлена: {cal} ккал в день")
    else:
        await message.answer("Пожалуйста, введите значение от 1000 до 4000")

@dp.message(F.text == "❌ Отменить")
async def cancel_action(message: types.Message):
    await message.answer("Действие отменено. Возвращаюсь в главное меню.", reply_markup=main_kb)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
