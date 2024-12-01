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
import re 
import threading 
import shutil

import vm_model
import compare_model
import parser 

bot = Bot(token="7544782847:AAFHEdr9zSDWVKmROIi4g_z7__X309SIqs0")
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

def compare_item(item_name, origin_path, folder_path):
    comparison_ratings = []
    response = compare_model.compare_images(item_name, origin_path, folder_path)
    json_response = json.loads(response)
    comparison_ratings = json_response["comparison_ratings"]
    comparison_ratings.sort(key=lambda item : item["rating"], reverse=True) 
    print(comparison_ratings[:5])
    return comparison_ratings[:5]

'''def compare_item(item_name, origin_path, folder_path):
    comparison_ratings = []
    response = compare_model.compare_images(item_name, origin_path, folder_path)
    json_response = json.loads(response)
    comparison_ratings = json_response["comparison_ratings"]
    comparison_ratings.sort(key=lambda item : item["rating"], reverse=True) 
    print(comparison_ratings[:5])
    return comparison_ratings[:5]'''

def get_item_messge(chat_id, description, comparison_ratings, items_urls):
    message = description + "\n\n"
    media = MediaGroupBuilder()
    for i in range(len(comparison_ratings)):
        image_path = comparison_ratings[i]#["image_url"]
        item_index = int(image_path.split("/")[-1].split("_")[0])
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
        print('parser:')
        items_urls = await parser.download_images(base_path+"/search_images/", search_phrase)
        print('end parser.')
        comparison_ratings = get_files(f"{base_path}/search_images/{search_phrase}/")
        return_message = get_item_messge(chat_id, description, comparison_ratings, items_urls)

        return return_message
    except:
        print(f"Exception caught")

    
from concurrent.futures import ThreadPoolExecutor
async def process_message(message: types.Message):
    filename = message.photo[-1].file_id
    base_path = f"./images/{message.from_user.id}" #{filename}.jpg"
    img_path = f"{base_path}/{filename}.jpg"
    await bot.download(message.photo[-1], destination=img_path)
    print('download')
    prompt = ""
    if(message.caption):
        prompt += "Я хочу чтообы ты нашел определенную вещь. " + message.caption
    else:
        prompt += "Найди все вещи. "
    response = await vm_model.get_description(img_path, prompt)
    print(response)
    print('vm')
    json_response = json.loads(response)
    items_size = len(json_response["items"])
    if(items_size==0):
        await message.answer("Не смог найти одежду на фотографии")
        return 

    tasks = []  
    with ThreadPoolExecutor() as executor:
        for i in range(items_size):
            try:
                search_phrase = json_response["items"][i]["search_phrase"]
                print(search_phrase)
                item_name = json_response["items"][i]["name"]
                description = json_response["items"][i]["description"]
                print('do_item:')
                tasks.append(await do_item(message.chat.id, base_path, filename, search_phrase, item_name, description))  
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
