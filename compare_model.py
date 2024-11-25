import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyAvszxQQyswlIPjT2AHBC458SvyH-kpIeQ")

system_instruction = \
'''
Ты ассистент, который сравнивает указанные элементы одежды, украшений и аксессуаров на фотографиях. Первая фотография является оригиналом, остальные ты должен поочередно сравнивать с ней. Указанный элемент на оригинальном фото и остальных сравнивай по следующим критериям:


для одежды:
тип
назначение или сезон (при наличии)
Предположительные косплеи (Если это может быть косплей, иначе не выводи этот пункт)
цвет
стили
бренд
Фактура материала
детали
декоративные элементы
покрой
особенности модели

для обуви:
тип
назначение или сезон (при наличии)
при наличии каблука: размеры, длина
цвет
стили
фактура материала
из чего это сделано
детали и декоративные элементы
вид застежки
Габариты
бренд


для украшений:
тип
форма
цвет
стили
из чего это сделано
из чего сделаны вставки и декоративные элементы 
детали
Габариты
бренд

для аксессуаров (каждый выводить отдельно):
тип
цвет
форма
стили
фактура материала
из чего это сделано
детали и декоративные элементы
вид застежки
Габариты
бренд

Для парфюма (если есть флакон, считать это парфюмом):
тип
предположительный аромат (для оригинала ты должен сам придумать это, исходя из образа, составленного другими элементами одежды на фото, для копий анализируй текст на картинке): верхние, средние, нижние ноты
стили
детали и декоративные элементы
Габариты
бренд


входные данные: 
1.название элемента  одежды, украшений и аксессуаров, сходство которого нужно анализировать
2.названия всех фотографий для сравнения, где первая фотография это оригинал
3.фотографии, где первая фотография это оригинал

формат ответа: 
Ты должен вернуть json формат с полем comparison_ratings, который является массивом с тремя полями. Первое называется "image_index", это индекс фотографии начиная с 0 (не считая оригинал). Второе называется "image_name", это название данной фотографии. Третье "image_url" url фотографии. Четвертое называется "rating", это ТОЛЬКО процент сходства от 1 до 100 с точностью до 1, например: 76
'''

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json"
}


model = genai.GenerativeModel(
    "gemini-1.5-flash", 
    generation_config=generation_config,
    system_instruction = system_instruction
)

def upload_multiple_images(image_paths):
    file_uris = []

    for image_path in image_paths:
        file = genai.upload_file(image_path)
        file_uris.append(file.uri)

    return file_uris

def compare_images(item, origin_filename, folder_path):
    files = []
    filenames = []
    files.append(origin_filename)
    filenames.append(origin_filename)
    for f in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, f)):
            files.append(os.path.join(folder_path, f))
            filenames.append(f)

    files_urls = upload_multiple_images(files)
    prompt = f"{item}\n\n images: {",".join(filenames)}"
    result = model.generate_content(
        [item, *files_urls]
    ) 
    result = model.generate_content([prompt])

    response = result.text.replace("```json", "")
    response = response.replace("```", "")
    print(response)
    return response 


# origin = "/home/koluchiy/Documents/Vision Match/Vision_match_bot/images/1087136471/2024-11-16_20:00:31.jpg"
# path = "/home/koluchiy/Documents/Vision Match/Vision_match_bot/images/1087136471/search_images/Серьги Van Cleef & Arpels с белыми цветами и камнями"
# print(compare_images("серьги", path, origin))