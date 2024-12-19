import os
import aiohttp
import asyncio


def get_basket(shirt_id):
    bascket = ''
    if 0 <= shirt_id <= 143:
        basket = '01'
    elif 144 <= shirt_id <= 287:
        basket = '02'
    elif 288 <= shirt_id <= 431:
        basket = '03'
    elif 432 <= shirt_id <= 719:
        basket = '04'
    elif 720 <= shirt_id <= 1007:
        basket = '05'
    elif 1008 <= shirt_id <= 1061:
        basket = '06'
    elif 1062 <= shirt_id <= 1115:
        basket = '07'
    elif 1116 <= shirt_id <= 1169:
        basket = '08'
    elif 1170 <= shirt_id <= 1313:
        basket = '09'
    elif 1314 <= shirt_id <= 1601:
        basket = '10'
    elif 1602 <= shirt_id <= 1655:
        basket = '11'
    elif 1656 <= shirt_id <= 1919:
        basket = '12'
    elif 1920 <= shirt_id <= 2045:
        basket = '13'
    elif 2046 <= shirt_id <= 2189:
        basket = '14'
    elif 2190 <= shirt_id <= 2405:
        basket = '15'
    elif 2406 <= shirt_id <= 2605:
        basket = '16'
    else:
        basket = '17'
    
    return basket

async def download_images(path, search_phrase):
<<<<<<< Updated upstream
    url = (f"https://aliexpress.ru/aer-webapi/v1/search")
    params= {
        "aeBrainIds": [],
        "catId": "",
        "pgChildren": [],
        "searchInfo": "",
        "searchText": "туфли",
        "searchTrigger": "",
        "source": "direct",
        "storeIds": []
=======
    url = (f"https://aliexpress.com/aer-webapi/v1/search")
    params= {
        "aeBrainIds": [],
"catId": "",
"pgChildren": [],
"searchInfo": "",
"searchText": "туфли",
"searchTrigger": "",
"source": "direct",
"storeIds": []
>>>>>>> Stashed changes
    }
          
                #    f"appType=1&curr=rub&dest=-1257786&page={1}"
                #f"&query={'%20'.join(search_phrase.split())}&resultset=catalog"
                #    f"&sort=popular&spp=24&suppressSpellcheck=false")
    #url = (f'https://aliexpress.ru/wholesale'
    #       f'?SearchText={"+".join(search_phrase.split())}'
    #       f'&page=1')
    async with aiohttp.ClientSession() as session:
<<<<<<< Updated upstream
        async with session.get(url,params=params) as response:
            print(await response.text())
            response_json = await response.json(content_type=None)
            print(response_json.text())
=======
        async with session.post(url,params=params) as response:
            print(response)
            response_json = await response.json(content_type=None)
            print(response_json)
>>>>>>> Stashed changes
            total_products = response_json["data"]["resultsCount"]
            print(total_products)
            search_size = 10 if total_products >= 10 else total_products
            products = response_json["data"]["products"][:search_size]

    urls = {}
    for i in range(search_size):
        id = products[i]["id"]
        name = products[i]["name"]
        short_id = id//100000 
        part = id//1000
        basket = get_basket(short_id)
        photo_url = f"https://basket-{basket}.wbbasket.ru/vol{short_id}/part{part}/{id}/images/big/1.webp"
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as response:
                #print(response)
                if not os.path.exists(f"{path}/{search_phrase}/"):
                    os.makedirs(f"{path}/{search_phrase}/")
                with open(f"{path}/{search_phrase}/{i}_{id}.jpg", "wb") as file:
                    file.write(await response.content.read())
                urls[i] = f"https://www.wildberries.ru/catalog/{id}/detail.aspx"
    return urls


asyncio.run(download_images('./images/1360934675/', 'Штаны кожаные'))