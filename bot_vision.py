import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import (
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# from config_reader import config

# Для записей с типом Secret* необходимо
# вызывать метод get_secret_value(),
# чтобы получить настоящее содержимое вместо '*****'
# Объект бота
# bot = Bot(token=config.bot_token.get_secret_value())
bot = Bot(token="")
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
"""@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")"""


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
            types.KeyboardButton(text="Нательное бельё"),
        ],
        [
            types.KeyboardButton(text="Бижутерия"),
            types.KeyboardButton(text="Аксессуары"),
        ],
        [
            types.KeyboardButton(text="Верхняя одежда"),
            types.KeyboardButton(text="Комбинированная"),
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
                text="Главный программист(почему?(всё хорошо(милфа)))",
                url="https://t.me/usumimin",
            )
        ],
        [
            InlineKeyboardButton(
                text="Аналитик данных(группа поддержки(профессиональный мемолог))",
                url="https://t.me/Gerpook",
            )
        ],
        [
            InlineKeyboardButton(
                text="Дизайнер(Физик-ядерщик(доминатрикс))",
                url="https://t.me/Niftylmao",
            )
        ],
        [
            InlineKeyboardButton(
                text="Тимлидер(pussy girl(pick me))", url="https://t.me/asmodeykaa"
            )
        ],
    ]
    urlkb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Контакты разработчиков:", reply_markup=urlkb)


@dp.message(F.text.lower() == "инструкция")
async def instruction(message: types.Message):
    await message.answer("Категория - фото - счастье")


@dp.message(Command("stop"))
async def stop_bot(message: types.Message):

    await message.answer("Бот остановлен.")
    await bot.close()
    await dp.stop_polling()


"""@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply('Это ответ с "ответом"')"""


@dp.message(F.text.lower() == "верх")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!", reply_markup=types.ReplyKeyboardRemove())


@dp.message(F.text.lower() == "а это?")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно!")


@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


"""
Для более динамической генерации кнопок можно воспользоваться сборщиком клавиатур. Нам пригодятся следующие методы:

add(<KeyboardButton>) — добавляет кнопку в память сборщика;
adjust(int1, int2, int3...) — делает строки по int1, int2, int3... кнопок;
as_markup() — возвращает готовый объект клавиатуры;
button(<params>) — добавляет кнопку с заданными параметрами, тип кнопки (Reply или Inline) определяется автоматически.
Создадим пронумерованную клавиатуру размером 4×4:

# новый импорт!
from aiogram.utils.keyboard import ReplyKeyboardBuilder

@dp.message(Command("reply_builder"))
async def reply_builder(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 17):
        builder.add(types.KeyboardButton(text=str(i)))
    builder.adjust(4)
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
"""
