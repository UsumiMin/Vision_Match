import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token="7544782847:AAGbpPxNuyvUT5TAyfMOge0SFb5G9QD2tIw")
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()
categories = {
    "Верх": 1,
    "Низ": 2,
    "Обувь": 3,
    "Комплекты": 4,
    "Акссесуары": 5,
    "Парфюмерия": 6,
}
categ = None


def one_of_categories(clothes):
    return categories[clothes]


# Хэндлер на команду /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Начать работу")],
        [
            types.KeyboardButton(text="Контакты"),
            types.KeyboardButton(text="Инструкция"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите действие"
    )

    await message.reply(
        "Привет!\nЯ Vision Match!\nВыбери из меню то, что хочешь сделать.",
        reply_markup=keyboard,
    )


@dp.message(F.text.lower() == "начать работу")
async def start_work(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Верх"), types.KeyboardButton(text="Низ")],
        [
            types.KeyboardButton(text="Обувь"),
            types.KeyboardButton(text="Комплекты"),
        ],
        [
            types.KeyboardButton(text="Аксессуары"),
            types.KeyboardButton(text="Парфюмерия"),
        ],
        [types.KeyboardButton(text="Назад")],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите категорию"
    )

    await message.reply(
        "Отлично! Выбери нужную категорию.",
        reply_markup=keyboard,
    )


@dp.message(F.text.lower() == "контакты")
async def url_command(message: types.Message):
    buttons = [
        [
            InlineKeyboardButton(
                text="Главный программист (Кривелева Катерина)",
                url="https://t.me/usumimin",
            )
        ],
        [
            InlineKeyboardButton(
                text="Аналитик данных (Селихова Таисия)",
                url="https://t.me/Gerpook",
            )
        ],
        [
            InlineKeyboardButton(
                text="Аналитик данных (Лобова Кристина)",
                url="https://t.me/Niftylmao",
            )
        ],
        [
            InlineKeyboardButton(
                text="Тимлидер (Кириченко Дана)", url="https://t.me/asmodeykaa"
            )
        ],
    ]

    urlkb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Контакты разработчиков:", reply_markup=urlkb)


@dp.message(F.text.lower() == "инструкция")
async def instruction(message: types.Message):
    await message.answer(
        "Выбираете категорию, загружаете нужное фото, бот подбирает вам ссылки с маркетплейсов с вашим товаром."
    )


@dp.message(Command("stop"))
async def stop_bot(message: types.Message):

    await message.answer("Бот остановлен.")
    await bot.close()
    await dp.stop_polling()


@dp.message(F.text.lower() == "верх")
async def with_puree(message: types.Message):
    await message.answer("Отправьте фото, на котором вы хотите найти одежду")


"""@dp.message(categ)
async def echo(message: types.Message):
    await message.answer("Отправьте фото, на котором вы хотите найти одежду")"""

global file_photo_id
# file_photo_id = ""
bot: Bot
global fp


@dp.message(F.photo)
async def send_photo_copy(message: types.Message):
    await message.answer(
        "Пока я без ии мало что могу( Но я отправлю ваше фото вам обратно."
    )
    await message.send_copy(chat_id=message.chat.id)


@dp.message(F.text)
async def send_photo(message: types.Message):
    await message.answer("Я не понимаю что вы хотите")
    """bot.send_photo(
        chat_id=message.from_user.id,
        photo=fp,
    )"""


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
