import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Токен не найден! Убедитесь, что файл .env существует и содержит BOT_TOKEN=...")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Reply-клавиатура ---
def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="Режим работы"), KeyboardButton(text="Контакты")],
        [KeyboardButton(text="Интересные документы"), KeyboardButton(text="Выставки")],
        [KeyboardButton(text="Как подать запрос?"), KeyboardButton(text="Задать вопрос")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- /start ---
@dp.message(CommandStart())
async def send_welcome(message: Message):
    await message.answer(
        "Привет! 👋 Я официальный бот Муниципального архива города Сургута.\n\n"
        "Выберите интересующую вас тему:",
        reply_markup=get_main_keyboard()
    )

# --- /help (опционально) ---
@dp.message(Command("help"))
async def send_help(message: Message):
    await send_welcome(message)

# --- Режим работы ---
@dp.message(lambda msg: msg.text == "Режим работы")
async def cmd_schedule(message: Message):
    await message.answer(
        "🕒 <b>Режим работы архива:</b>\n"
        "Пн–Пт: 9:00–17:12\n"
        "Обед: 13:00–14:00\n"
        "Сб, Вс — выходной"
    )

# --- Контакты ---
@dp.message(lambda msg: msg.text == "Контакты")
async def cmd_contacts(message: Message):
    await message.answer(
        "📍 <b>Контактная информация:</b>\n"
        "Адрес: г. Сургут, ул. Мелик-Карамова, д. 4/4\n"
        "Телефон приёмной: +7 (3462) 550-496\n"
        "Email: arhiv@admsurgut.ru"
    )

# --- Интересные документы ---
@dp.message(lambda msg: msg.text == "Интересные документы")
async def cmd_documents(message: Message):
    await message.answer(
        "📜 <b>Интересные архивные документы:</b>\n\n"
        "• <b>10.12.1930</b> — постановление об образовании "
        "<b>Остяко-Вогульского национального округа</b> — основы современного ХМАО–Югры.\n\n"
        "• <b>04.02.1925</b> — выписка о <b>понижении статуса Сургута до сельского поселения</b>."
    )

# --- Выставки ---
@dp.message(lambda msg: msg.text == "Выставки")
async def cmd_exhibitions(message: Message):
    await message.answer(
        "🖼️ <b>Актуальные выставки:</b>\n\n"
        "• «Сургутские грани» — 16.06.2025\n"
        "• «Великая Победа» — 25.04.2025\n"
        "• «День геолога» — 06.04.2025\n"
        "• «Раритеты Югры» — 21.03.2025"
    )

# --- Как подать запрос? ---
@dp.message(lambda msg: msg.text == "Как подать запрос?")
async def cmd_request(message: Message):
    await message.answer(
        "ℹ️ Официальные архивные справки и копии документов оформляются "
        "<b>только через портал Госуслуг</b>:\n"
        "🔗 https://www.gosuslugi.ru/600149/1/form"
    )

# --- Задать вопрос (простая логика) ---
user_feedback_mode = set()

@dp.message(lambda msg: msg.text == "Задать вопрос")
async def cmd_feedback(message: Message):
    user_feedback_mode.add(message.from_user.id)
    await message.answer(
        "💬 Напишите ваш вопрос.\n\n"
        "<b>Внимание!</b> Сообщения с персональными данными "
        "(ФИО, паспорт, ИНН и т.д.) <b>не рассматриваются</b>."
    )

# --- Универсальный обработчик (только для НЕ кнопок и НЕ команд) ---
@dp.message()
async def handle_other(message: Message):
    # Игнорируем пустые и не-текстовые сообщения
    if not message.text:
        return

    # Если пользователь в режиме вопроса — принимаем ответ
    if message.from_user.id in user_feedback_mode:
        user_feedback_mode.discard(message.from_user.id)
        logging.info(f"Вопрос от {message.from_user.id}: {message.text}")
        await message.answer("Спасибо за вопрос! Для официальных запросов используйте портал Госуслуг.")
    # Если это команда (начинается с /) — не поддерживаем (кроме /start и /help, они уже обработаны)
    elif message.text.startswith("/"):
        await message.answer("Команда не распознана. Используйте кнопки меню или /start.")
    # Любое другое сообщение — просим использовать кнопки
    else:
        await message.answer(
            "Пожалуйста, используйте кнопки меню.\n"
            "Я не обрабатываю персональные данные."
        )

# --- Запуск ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())