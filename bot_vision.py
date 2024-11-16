import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token='')
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()


class ai:
    categories = 0

    def send_to_ai(photo):
        pass

    def take_from_ai(category):
        pass


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
    await message.answer("Отправьте фото, на котором вы хотите найти одежду")


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


bot: Bot


@dp.message(F.photo)
async def send_photo(message: types.Message):
    file_name = f"./{message.photo[-1].file_id}.jpg"
    kb = [[types.KeyboardButton(text="Выбрать всё")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Нажмите на кнопку или введите нужную категорию",
    )
    ai.send_to_ai(file_name)
    await message.reply(
        "Скажите что вы хотите найти",
        reply_markup=keyboard,
    )
    # bot.download(message.photo[-1],destination=file_name)


@dp.message(F.text.lower() == "выбрать всё")
async def ai_all(message: types.Message):
    ai.take_from_ai("all")
    await message.reply("Ищу всё, вот оно: (В процессе)")


@dp.message(F.text)
async def ai_one(message: types.Message):
    ai.take_from_ai(F.text.lower())
    await message.reply(f"Ищу {message.text.lower()}, вот оно: (В процессе)")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
