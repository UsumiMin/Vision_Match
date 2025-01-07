import os
import aiohttp
import itertools

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time

  

class Parser:
    search_size = 5
    image_count = itertools.count()

    def __init__(self, search_phrase, path):
        self.search_phrase = search_phrase
        self.path = path

        if not os.path.exists(f"{path}/"):
            os.makedirs(f"{path}/")

    async def download_image(self, url, filename):
        async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    with open(f"{self.path}/{filename}", "wb") as file:
                        file.write(await response.content.read())

class ParserWb(Parser):
    
    def __init__(self, search_phrase, path):
        super().__init__(search_phrase, path)

    async def get_products(self, search_phrase):
        url = (f"https://search.wb.ru/exactmatch/ru/common/v4/search?"
                    f"appType=1&curr=rub&dest=-1257786&page={1}"
                    f"&query={'%20'.join(search_phrase.split())}&resultset=catalog"
                    f"&sort=popular&spp=24&suppressSpellcheck=false")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_json = await response.json(content_type=None)
                total_products = response_json["data"]["total"]
                search_size = self.search_size if total_products >= self.search_size else total_products
                products = response_json["data"]["products"][:search_size]

        return products

    def get_basket(self, productId):
        bascket = ''
        if 0 <= productId <= 143:
            basket = '01'
        elif 144 <= productId <= 287:
            basket = '02'
        elif 288 <= productId <= 431:
            basket = '03'
        elif 432 <= productId <= 719:
            basket = '04'
        elif 720 <= productId <= 1007:
            basket = '05'
        elif 1008 <= productId <= 1061:
            basket = '06'
        elif 1062 <= productId <= 1115:
            basket = '07'
        elif 1116 <= productId <= 1169:
            basket = '08'
        elif 1170 <= productId <= 1313:
            basket = '09'
        elif 1314 <= productId <= 1601:
            basket = '10'
        elif 1602 <= productId <= 1655:
            basket = '11'
        elif 1656 <= productId <= 1919:
            basket = '12'
        elif 1920 <= productId <= 2045:
            basket = '13'
        elif 2046 <= productId <= 2189:
            basket = '14'
        elif 2190 <= productId <= 2405:
            basket = '15'
        elif 2406 <= productId <= 2605:
            basket = '16'
        else:
            basket = '17'
        
        return basket


    def get_photo_url(self, productId):
        short_id = productId//100000 
        part = productId//1000
        basket = self.get_basket(short_id)
        photo_url = f"https://basket-{basket}.wbbasket.ru/vol{short_id}/part{part}/{productId}/images/big/1.webp"
        return photo_url

    async def parse(self):
        products = await self.get_products(self.search_phrase)
        urls = {}
        for i in range(self.search_size):
            id = products[i]["id"]
            photo_url = self.get_photo_url(id)
            image_index = int(next(self.image_count))
            filename = f"{image_index}.jpg"
            await self.download_image(photo_url, filename)
            urls[image_index] = f"https://www.wildberries.ru/catalog/{id}/detail.aspx"
        return urls
    

class ParserOzon(Parser):
    def __init__(self, search_phrase, path):
        super().__init__(search_phrase, path)

    async def download(self, urls):
        print(urls)
        for i, url in urls.items():
            await self.download_image(url, f"{i}.jpg")

    async def parse(self):
        #options = Options()
        #options.add_argument("--headless")
        driver = uc.Chrome(version_main=128)
        driver.implicitly_wait(10)
        urls = {}
        urls_img = {}
        try:
            driver.get("https://www.ozon.ru")
            time.sleep(5)
            find_goods = driver.find_element(By.NAME, 'text')
            find_goods.clear()
            time.sleep(2)
            find_goods.send_keys(self.search_phrase)
            time.sleep(4)
            find_goods.send_keys(Keys.ENTER)
            time.sleep(4)
            try:
                find_goods = driver.find_elements(By.CLASS_NAME, 'iw1_23')[:5]
            except:
                pass
            for el in find_goods:
                el.click()
                time.sleep(1)
            time.sleep(6)
            for el in find_goods:
                try:
                    driver.switch_to.window(driver.window_handles[-1])
                except:
                    pass
                time.sleep(6)
                # Получение HTML-кода страницы
                page_source = str(driver.page_source)
                # Создание объекта BeautifulSoup для парсинга HTML-кода
                soup = BeautifulSoup(page_source, 'html.parser')
                # работа с html
                # Получение названия товара
                name_element = soup.h1
                name = name_element.text.strip().replace('"', "&quot;") if name_element else 'No name'
                print(name)
                # Получение URL первой картинки если первое видео
                if soup.find('div', {"data-widget": "webGallery"}).find('video-player') or soup.find('div', {"data-widget": "webGallery"}).find('video'):
                    print('video')
                    find_img = driver.find_element(By.XPATH, '//*[@data-index="1"]').find_element(By.TAG_NAME, 'img')
                    find_img.click()
                    time.sleep(2)
                    page_source = str(driver.page_source)
                    soup = BeautifulSoup(page_source, 'html.parser')
                else:
                    # Получение URL первой картинки
                    print('photo')
                image_element = soup.select(f'img[alt*="{name[:30]}"]')
                print(image_element)
                image_url = image_element[0].get('src') if image_element else ''
                image_index = int(next(self.image_count))
                urls_img[image_index] = image_url
                urls[image_index] = driver.current_url
                driver.close()

            # Получение URL страницы с товаром
        except Exception as ex:
            print(ex)
        finally:
            try:
                driver.switch_to.window(driver.window_handles[0])
                driver.close()
            except:
                pass
            driver.quit()
            await self.download(urls_img)
        return urls
 
async def parse_shops(search_phrase, path):
    shops = [ParserWb, ParserOzon]
    urls = {}
    for shop_parser in shops:
        urls.update(await shop_parser(search_phrase, path).parse())
    
    return urls
