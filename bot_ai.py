import asyncio
import logging
import emoji

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums.parse_mode import ParseMode

import os
import datetime
import json
import shutil

from ai_models import VisionModel, ComparisonModel
import parsers

vision_model = VisionModel()
comparison_model = ComparisonModel()

# Подключаем телеграмм-бота с помощью токена
bot = Bot(token="7544782847:AAE6tRKg-ghUnr_elfnpLG8KhC_IAkDzoHg")

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    """Функция для отправки привественного сообщения

    В этой функции пользователю отправляется приветсвенное сообщение, 
    а также создаётся клавиатура для выбора последующего действия.

    Args:
        message (types.Message): Сообщение с командой "start"
    """

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
    
    if(not os.path.isdir(f"./images/{message.from_user.id}")):
        os.mkdir(f"./images/{message.from_user.id}")

    
    await message.reply(
        emoji.emojize(
            "Привет!:waving_hand: \n\nМеня зовут *Vision Match!* Я – ваш помощник в мире моды! :woman_dancing::man_dancing:"
            " \nКак это работает? Просто отправьте мне фотографию или рисунок одежды, и я найду лучшие варианты на маркетплейсах!"
            " \n\nДавайте начнём работу!"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


@dp.message(F.text.lower() == "начать работу")
async def start_work(message: types.Message):
    """Функция для ответа на сообщение "начать работу"

    Args:
        message (types.Message): сообщение "начать работу"
    """

    kb = [
        [
            types.KeyboardButton(text="Искать все"),
            types.KeyboardButton(text="Искать отдельную вещь"),
        ],
        [   types.KeyboardButton(text="Назад") ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите режим"
    )

    await message.reply(
        "Выберите режим работы бота: поиск всех вещей с фотографии или поиск определенной вещи",
        reply_markup=keyboard,
    )


@dp.message(F.text.lower() == "контакты")
async def url_command(message: types.Message):
    """Функция для вывода контактов разработчиков

    Args:
        message (types.Message): сообщение "контакты"
    """
    
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
    """Функция для отправки инструкции по работе с ботом

    Args:
        message (types.Message): сообщение "инструкция"
    """

    await message.answer(
        "1. Выбираете режим: \"искать все \" или \"искать отдельную вещь\" \n"
        "2. Загружаете нужное фото, если вы выбирали категорию \"искать отдельную вещь\""
        ", необходимо указать, какой именно элемент вы хотите найти \n"
        "3. Бот отправляет сообщение с описанием по тегам, фото и ссылками с маркетплейсов для каждого из товаров, который нужно было найти."
    )


@dp.message(F.text.lower() == "искать все")
async def looking_for_all(message: types.Message):
    """Функция для вывода ответа на сообщение "искать все"

    Args:
        message (types.Message): сообщение "искать все"
    """
    
    await message.answer("Отправьте фото, на котором вы хотите найти одежду и аксессуары")

@dp.message(F.text.lower() == "искать отдельную вещь")
async def looking_for_thing(message: types.Message):
    """Функция для вывода ответа на сообщение "искать отдельную вещь"

    Args:
        message (types.Message): сообщение "искать отдельную вещь"
    """

    await message.answer("Отправьте фото с указанием элемента, который вы хотите найти")


@dp.message(F.text.lower() == "назад")
async def url_command(message: types.Message):
    """Функция для возвращения к приветсвию

    Args:
        message (types.Message): сообщение "назад"
    """

    await send_welcome(message)

async def compare_response(item_name, origin_path, folder_path):
    """Функция для получения списка фотографий, прошедших сравнение на совпадение с оригиналом

    Args:
        item_name (str): название предмета
        origin_path (str): путь к оригинальной фотографии
        folder_path (str): путь к папке с фотографиями для сравнения

    Returns:
        list: Список фотографий
    """

    comparison_ratings = []
    response = await comparison_model.compare_images(item_name, origin_path, folder_path)
    json_response = json.loads(response)
    for item in json_response["comparison_ratings"]:
        comparison_ratings.append(item["image_path"])

    return comparison_ratings[:5]

def get_item_messge(description, comparison_ratings, items_urls):
    """Функция для составления сообщения с описанием предмета и добавления фото

    Args:
        description (str): описание предмета
        comparison_ratings (list): список фотографий
        items_urls (list): список ссылок в магазины

    Returns:
        tuple: кортеж из фото и текста описания
    """

    message = description + "\n\n"
    media = MediaGroupBuilder()
    for i in range(len(comparison_ratings)):
        image_path = comparison_ratings[i]
        item_index = int(image_path.split("/")[-1].split(".")[0])
        url = items_urls[item_index]
        message += f"{i+1}. {url} \n"
        try:
            media.add_photo(types.FSInputFile(image_path), caption=url)
        except ...:
            print("Caught exception while loading photo")
            continue
    return (media, message)

async def do_item(base_path, origin_filename, search_phrase, item_name, description):
    """Функция для сбора фотографий и ссылок на них в одно сообщение

    Args:
        base_path (str): путь до папки с id пользователя
        origin_filename (str): путь до оригинальной фотографии
        search_phrase (str): фраза для поиска
        item_name (str): название предмета
        description (str): описание предмета

    Returns:
        tuple: кортеж из фото и текста описания
    """

    try:
        all_filters = await parsers.ParserWb.get_filters(item_name)
        prompt = f"режим фильтры \n\n входные данные для режима: \n {item_name}\n\n {all_filters}"
        
        ai_filters_response = await vision_model.get_filters(origin_filename, prompt, all_filters)
        filters_reponse = json.loads(ai_filters_response)
        print(filters_reponse)
        url_filters = ""
        if filters_reponse.get("filters"):
            url_filters = filters_reponse["filters"]

        folder = f"{base_path}/search_images/{search_phrase}/"
        items_urls = await parsers.parse_shops(search_phrase, folder, url_filters)
        comparison_ratings = await compare_response(item_name, origin_filename, folder)
        return_message = get_item_messge(description, comparison_ratings, items_urls)

        return return_message
    except Exception as e:
        print(f"Caught exception: {e}")
    
async def process_message(message: types.Message):
    """Функция для обработки сообщения от пользователя

    В этой функции загружается фотография от пользователя, а также её описание.
    Далее функция получает ответ от ИИ и обрабатывает каждый элемент на фотографии.
    После этого бот отправляет финальное сообщение пользователю.

    Args:
        message (types.Message): сообщение с фотографией
    """

    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    base_path = f"./images/{message.from_user.id}"
    img_path = f"{base_path}/{filename}.jpg"
    await bot.download(message.photo[-1], destination=img_path)
    prompt = "режим описание \n\n "
    if(message.caption):
        prompt += "входные данные для режима: \n " + message.caption 
    response = await vision_model.get_description(img_path, prompt)
    print(response)
    json_response = json.loads(response)
    items_size = len(json_response["items"])

    if (json_response.get("error_message")):
        # Если ИИ возвращает ошибку, то передаём её содержание пользователю
        await message.answer(json_response["error_message"])
        return 
    
    if(items_size==0):
        # Если ИИ не нашла запрошенные объекты, то просим пользователя загрузить другую фотографию
        error_message = "К сожалению, я не смог найти указанный элемент на вашем изображении."
        " Пожалуйста, попробуйте загрузить другое изображение или выберите более четкий ракурс."
        await message.answer(error_message)
        return 
    
    if(items_size >= 10):
        # Если ИИ нашла больше 10 объектов на фото, то сообщаем пользователю, что работа бота займёт много времени
        wait_please_msg = "На вашем изображении больше 10 элементов, их поиск может занять много времени. "
        "Вы уверены, что хотите продолжить?"
        await message.answer(wait_please_msg)
        
    tasks = []  
    for i in range(items_size):
        # Цикл для работы с каждым отдельным предметом на фото
        try:
            search_phrase = json_response["items"][i]["search_phrase"]
            print(search_phrase)
            item_name = json_response["items"][i]["name"]
            description = json_response["items"][i]["description"]
            tasks.append(do_item(base_path, img_path, search_phrase, item_name, description))  
        except Exception as e:
            print(f"Exception on item {item_name} with error {e}")
            continue

    
    results = await asyncio.gather(*tasks)
    #for i in range(items_size):
    for result in results:
        # Цикл для отправки готовых сообщений с каждым отдельным предметом на фото
        try:
            media, result_message = result
            await bot.send_media_group(message.chat.id, media=media.build())
            await bot.send_message(message.chat.id, result_message)#, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(f"Couldn't send message with index {i} because {e}")
    
    # Удаление фотографий после окончания работы
    if(os.path.isdir(f"{base_path}/search_images/")):
        shutil.rmtree(f"{base_path}/search_images/")
    if(os.path.isfile(img_path)):
        os.remove(img_path)


@dp.message(F.photo)
async def send_photo(message: types.Message):
    """Функция для начала работы с фотографией

    Args:
        message (types.Message): Сообщение с фотографией
    """

    try:
        asyncio.create_task(process_message(message))
        await message.reply("Начал поиск...")
    except:
        print(f"Exception in request processing")
        await message.reply("Извините, что-то пошло не так. Я не смог обработать вашу фотографию, попробуйте повторить ваш запрос. ")

@dp.message(F.text)
async def send_dont_understand(message: types.Message):
    """функция для ответа бота на незнакомые команды

    Args:
        message (types.Message): текст от пользователя
    """

    await message.answer("Я не понимаю что вы хотите")

# Запуск процесса поллинга новых апдейтов
async def main():
    """Функция для запуска процесса поллинга апдейтов бота"""
    
    if not os.path.exists(f"./images/"):
        os.makedirs(f"./images/")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
