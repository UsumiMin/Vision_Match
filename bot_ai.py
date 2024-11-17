import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder

import os
import datetime
import json
import re 
import threading 

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
        "Привет!\nЯ Vision Match!\nВыбери из меню то, что хочешь сделать.",
        reply_markup=keyboard,
    )


@dp.message(F.text.lower() == "начать работу")
async def start_work(message: types.Message):
    # kb = [
    #     [
    #         types.KeyboardButton(text="Все"),
    #         types.KeyboardButton(text="Отдельную вещь"),
    #     ]
    # ]
    # keyboard = types.ReplyKeyboardMarkup(
    #     keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите режим"
    # )

    await message.reply(
        "Загрузи фотку"#,
        #reply_markup=keyboard,
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


@dp.message(F.text.lower() == "верх")
async def with_puree(message: types.Message):
    await message.answer("Отправьте фото, на котором вы хотите найти одежду")

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

async def do_item(chatid, base_path, origin_filename, search_phrase, item_name, description):
    items_urls = parser.download_images(base_path+"/search_images/", search_phrase)
    print("+"*50, "parser finished")
    comparison_ratings = get_files(f"{base_path}/search_images/{search_phrase}/")
    #comparison_ratings = compare_item(item_name, #compare_model.comparse_image(item_name, 
    #                   f"{base_path}/{origin_filename}.jpg", 
    #                   f"{base_path}/search_images/{search_phrase}/")
    print(items_urls)
    #threading.Thread(target=send_result_match, args=(chatid, description, comparison_ratings, items_urls)).start()
        
    #loop = asyncio.get_event_loop()
    #result = await loop.run_in_executor(None, send_result_match, chatid, description, comparison_ratings, items_urls)

    #asyncio.create_task(send_result_match(chatid, description, comparison_ratings, items_urls))
    await send_result_match(chatid, description, comparison_ratings, items_urls)
    #result = await asyncio.to_thread(send_result_match, chatid, description, comparison_ratings, items_urls)
        

async def process_message(message: types.Message):
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    base_path = f"./images/{message.from_user.id}" #{filename}.jpg"
    img_path = f"{base_path}/{filename}.jpg"
    await bot.download(message.photo[-1], destination=img_path)
    response = vm_model.get_description(img_path)
    print(response)
    json_response = json.loads(response)
    items_size = len(json_response["items"])
    if(items_size==0):
        await message.answer("Не смог найти одежду на фотографии")

    items = []
    threads = []
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
            await do_item(message.chat.id, base_path, filename, search_phrase, item_name, description)
        except:
            print(f"Exception on item {item_name}")
        # items_urls = parser.download_images(base_path+"/search_images/", search_phrase)
        # comparison_ratings = compare_item(item_name, #compare_model.comparse_image(item_name, 
        #                                          f"{base_path}/{filename}.jpg", 
        #                                          f"{base_path}/search_images/{search_phrase}/")
        # print(items_urls)
        # await send_result_match(message.chat.id, description, comparison_ratings, items_urls)
    
    # for thread in threads:
    #     thread.join()

    return "Ready"


@dp.message(F.photo)
async def send_photo_copy(message: types.Message):
    print(f"Received message: {message.text}")
    #result = await process_message(message)  # Do NOT use asyncio.to_thread
    #await message.answer(result)
    asyncio.create_task(process_message(message))

    #result = await asyncio.to_thread(process_message, message)
    #await message.answer(result)
    # loop = asyncio.get_event_loop()
    # result = await loop.run_in_executor(None, process_message, message)

    # await message.reply(result)
    
    # thread = threading.Thread(target=process_message_thread, args=(message,))
    # thread.start()

    await message.reply("Message received and processing started...")
'''
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    base_path = f"./images/{message.from_user.id}" #{filename}.jpg"
    img_path = f"{base_path}/{filename}.jpg"
    await bot.download(message.photo[-1], destination=img_path)
    response = vm_model.get_description(img_path)
    print(response)
    json_response = json.loads(response)
    items_size = len(json_response["items"])
    if(items_size==0):
        await message.answer("Не смог найти одежду на фотографии")

    comparison_ratings = []
    #threads = []
    for i in range(items_size):
        search_phrase = json_response["items"][i]["search_phrase"]
        item_name = json_response["items"][i]["name"]
        description = json_response["items"][i]["description"]
        items_urls = await parser.download_images(base_path+"/search_images/", search_phrase)
        comparison_ratings = await compare_item(item_name, #compare_model.comparse_image(item_name, 
                                                 f"{base_path}/{filename}.jpg", 
                                                 f"{base_path}/search_images/{search_phrase}/")
        print(items_urls)
        #threads.append(threading.Thread(send_result_match, args=(message.chat.id, description, comparison_ratings, items_urls)))
        #await threads[i].start()
        await send_result_match(message.chat.id, description, comparison_ratings, items_urls)
    
        #await send_result_match(message.chat.id, description, comparison_ratings, items_urls)
'''  

def long_running_function(message):
    # Perform your time-consuming task here
    print("Starting long-running function...")
    # Simulate a long-running task
    asyncio.sleep(5)
    print("Long-running function completed!")
    return "Result from long-running function"

@dp.message(F.text.lower() == 'long_task')
async def handle_long_task(message: types.Message):
    # Run the function in a new thread
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, long_running_function, message)

    # Send the result back to the user
    await message.reply(result)

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
