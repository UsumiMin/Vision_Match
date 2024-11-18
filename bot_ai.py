import asyncio
import logging
import emoji

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder

import os
import datetime
import json
import re 
import threading 
import shutil

import vm_model
import compare_model
import parser 


bot = Bot(token="7544782847:AAGbpPxNuyvUT5TAyfMOge0SFb5G9QD2tIw")
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
        "Выбираете категорию, загружаете нужное фото, бот подбирает вам ссылки с маркетплейсов с вашим товаром."
    )


@dp.message(F.text.lower() == "искать все")
async def with_puree(message: types.Message):
    await message.answer("Отправьте фото, на котором вы хотите найти одежду")

@dp.message(F.text.lower() == "искать отдельную вещь")
async def with_puree(message: types.Message):
    await message.answer("Отправьте фото с описвнием что конкретно вы хотите найти с фотографии ")


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

async def send_result_match(chat_id, description, comparison_ratings, items_urls):
    message = description + "\n\n"
    media = MediaGroupBuilder()
    for i in range(len(comparison_ratings)):
        #item_index = comparison_ratings[i]["image_name"].split("_")[0]
        #if(len(item_index)):
        #    continue
        #item_index = int(item_index)
        image_path = comparison_ratings[i]#["image_url"]
        item_index = int(image_path.split("/")[-1].split("_")[0])
        url = items_urls[item_index]
        message += f"{i+1}. {url} \n"
        try:
            media.add_photo(types.FSInputFile(image_path), caption=url)#url)
        except ...:
            print("Caight exception while loading photo")
            continue
    #await bot.send_media_group(chat_id, media_group)
    try:
        await bot.send_media_group(chat_id, media=media.build())
        await bot.send_message(chat_id, message)
    except ...:
        print("Caight exception while sending group")


def get_files(folder_path):
    files = []
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            files.append(os.path.join(folder_path, f))

    return files[:5]

async def do_item(chat_id, base_path, origin_filename, search_phrase, item_name, description):
    try:
        items_urls = parser.download_images(base_path+"/search_images/", search_phrase)
        comparison_ratings = get_files(f"{base_path}/search_images/{search_phrase}/")
        
        await send_result_match(chat_id, description, comparison_ratings, items_urls)
    except:
        print(f"Exception caught")

    if(os.path.isdir(f"{base_path}/search_images/{search_phrase}")):
        shutil.rmtree(f"{base_path}/search_images/{search_phrase}")
        #os.rmdir(f"{base_path}/search_images/")
    

async def process_message(message: types.Message):
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    base_path = f"./images/{message.from_user.id}" #{filename}.jpg"
    img_path = f"{base_path}/{filename}.jpg"
    await bot.download(message.photo[-1], destination=img_path)
    prompt = ""
    if(message.caption):
        prompt += "Я хочу чтообы ты нашел определенную вещь. " + message.caption 
    response = vm_model.get_description(img_path, prompt)
    print(response)
    json_response = json.loads(response)
    items_size = len(json_response["items"])
    if(items_size==0):
        await message.answer("Не смог найти одежду на фотографии")
        return 


    tasks = []  # Create a list to hold the tasks
    for i in range(items_size):
        search_phrase = json_response["items"][i]["search_phrase"]
        print(search_phrase)
        item_name = json_response["items"][i]["name"]
        description = json_response["items"][i]["description"]
        # thread = threading.Thread(target=do_item, args=(message.chat.id, base_path, filename,
        #                                         search_phrase, item_name, description))
        # threads.append(thread)
        # thread.start()
        #result = await asyncio.to_thread(do_item, message.chat.id, base_path, filename,
        #                                       search_phrase, item_name, description)
        try:
            # threading.Thread(target=do_item, args=(message.chat.id, base_path, filename,
            #                                      search_phrase, item_name, description)).start()
        
            await do_item(message.chat.id, base_path, filename, search_phrase, item_name, description)
            #result = await asyncio.to_thread(do_item, message.chat.id, base_path, filename,
            #                                 search_phrase, item_name, description)
            #task = asyncio.create_task(do_item(message.chat.id, base_path, filename, search_phrase, item_name, description)) # Create a task
           # tasks.append(task)  # Add task to the list
     
        except:
           print(f"Exception on item {item_name}")
           continue

    #await asyncio.gather(*tasks) # Await all tasks concurrently
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
