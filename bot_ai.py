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

bot = Bot(token="7911900370:AAH8I5skyucy8wXUXPYLB4x3tNsgl0CJxiE")
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Диспетчер
dp = Dispatcher()

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
    
    if(not os.path.isdir(f"./images/{message.from_user.id}")):
        os.mkdir(f"./images/{message.from_user.id}")

    
    await message.reply(
        emoji.emojize(
            "Привет!:waving_hand: \n\nМеня зовут *Vision Match!* Я – ваш помощник в мире моды! :woman_dancing::man_dancing: \nКак это работает? Просто отправьте мне фотографию или рисунок одежды, и я найду лучшие варианты на маркетплейсах! \n\nДавайте начнём работу!"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )


@dp.message(F.text.lower() == "начать работу")
async def start_work(message: types.Message):
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
        "1. Выбираете режим: \"искать все \" или \"искать отдельную вещь\" \n2. Загружаете нужное фото, если вы выбирали категорию \"искать отдельную вещь\", необходимо указать, какой именно элемент вы хотите найти \n3. Бот отправляет сообщение с описанием по тегам, фото и ссылками с маркетплейсов для каждого из товаров, кототорый нужно было найти."
    )


@dp.message(F.text.lower() == "искать все")
async def with_puree(message: types.Message):
    await message.answer("Отправьте фото, на котором вы хотите найти одежду и аксессуары")

@dp.message(F.text.lower() == "искать отдельную вещь")
async def with_puree(message: types.Message):
    await message.answer("Отправьте фото с указанием элемента, который вы хотите найти")


@dp.message(F.text.lower() == "назад")
async def url_command(message: types.Message):
    await send_welcome(message)

async def compare_response(item_name, origin_path, folder_path):
    comparison_ratings = []
    response = await comparison_model.compare_images(item_name, origin_path, folder_path)
    json_response = json.loads(response)
    for item in json_response["comparison_ratings"]:
        comparison_ratings.append(item["image_path"])

    return comparison_ratings[:5]

def get_item_messge(chat_id, description, comparison_ratings, items_urls):
    message = description + "\n\n"
    media = MediaGroupBuilder()
    print(items_urls)
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


def get_files(folder_path):
    files = []
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            files.append(os.path.join(folder_path, f))

    return files[:5]

async def do_item(chat_id, base_path, origin_filename, search_phrase, item_name, description):
    try:
        items_urls = await parsers.parse_shops(search_phrase, f"{base_path}/search_images/{search_phrase}/")
        comparison_ratings = await compare_response(item_name, origin_filename, f"{base_path}/search_images/{search_phrase}/")
        return_message = get_item_messge(chat_id, description, comparison_ratings, items_urls)

        return return_message
    except:
        print(f"Exception caught")
    
async def process_message(message: types.Message):
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    base_path = f"./images/{message.from_user.id}" #{filename}.jpg"
    img_path = f"{base_path}/{filename}.jpg"
    await bot.download(message.photo[-1], destination=img_path)
    prompt = "режим описание \n\n "
    if(message.caption):
        prompt += "входные данные для режима: \n " + message.caption 
    response = await vision_model.get_description(img_path, prompt)
    # response = vm_model.get_description(img_path, prompt)
    print(response)
    json_response = json.loads(response)
    items_size = len(json_response["items"])
    if (json_response.get("error_message")):
        await message.answer(json_response["error_message"])
        return 

    if(items_size==0):
        error_message = "К сожалению, я не смог найти указанный элемент на вашем изображении. Пожалуйста, попробуйте загрузить другое изображение или выберите более четкий ракурс."
        await message.answer(error_message)
        return 
    
    if(items_size >= 10):
        wait_please_msg = "На вашем изображении больше 10 элементов, их поиск может занять много времени. Вы уверены, что хотите продолжить?"
        await message.answer(wait_please_msg)
        
    tasks = []  
    for i in range(items_size):
        try:
            search_phrase = json_response["items"][i]["search_phrase"]
            print(search_phrase)
            item_name = json_response["items"][i]["name"]
            description = json_response["items"][i]["description"]
            tasks.append(await do_item(message.chat.id, base_path, img_path, search_phrase, item_name, description))  
        except:
            print(f"Exception on item {item_name}")
            continue

    for i in range(items_size):
        try:
            media, result_message = tasks[i][0], tasks[i][1]
            await bot.send_media_group(message.chat.id, media=media.build())
            await bot.send_message(message.chat.id, result_message, parse_mode=ParseMode.MARKDOWN)
        except:
            print(f"Couldn't send message with index {i}")

    if(os.path.isdir(f"{base_path}/search_images/")):
        shutil.rmtree(f"{base_path}/search_images/")
    if(os.path.isfile(img_path)):
        os.remove(img_path)


@dp.message(F.photo)
async def send_photo_copy(message: types.Message):
    try:
        asyncio.create_task(process_message(message))
        await message.reply("Начал поиск...")
    except:
        print(f"Exception in request processing")
        await message.reply("Извините, что-то пошло не так. Я не смог обработать вашу фотографию, попробуйте повторить ваш запрос. ")

@dp.message(F.text)
async def send_photo(message: types.Message):
    await message.answer("Я не понимаю что вы хотите")

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
