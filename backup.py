"""
1) Для того чтобы получить token_VK использовать:
from urllib.parse import urlencode

id_app = '51817896'
oauth_base_url = 'https://oauth.vk.com/authorize'
params = {
    'client_id': id_app,
    'redirect_uri': 'https://oauth.vk.com/blank.html',
    'display': 'page',
    'scope': 'photos',
    'response_type': 'token'
}

oauth_url = f'{oauth_base_url}?{urlencode(params)}'
print(oauth_url)
Перейти по полученной ссылке и скопировать из адресной строки - token_VK.

2) Для того, чтобы вызвать скрипт, нужно открыть терминал и прописать команду:
'python название_файла user_id token_yd'.
Пример: python backup.py 123456789 y0_Aklfgbfhlbflbdlbclbdlbvndlfjsk
"""

import json
import logging
import sys

from vk_api_client import VKAPIClient
from yandex_disk_api_client import YandexDiskAPIClient

# логирование
logger = logging.getLogger()
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s")
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s")
)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def create_json_file(photo_info):
    """Сохранение инфо по фотографиям в json-файл"""
    list_sizes = []

    for file_name, info in photo_info.items():
        dict_size = {'file_name': file_name, 'size': info['size']}
        list_sizes.append(dict_size)

    with open('result_info.json', 'w') as f:
        json.dump(list_sizes, f, indent=2)


# подставить токен, полученный из VK
token_VK = ''

if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) != 3:
        raise Exception('Call the script and enter 2 arguments')

    user_id = arguments[1]
    token_yd = arguments[2]

    vk_client = VKAPIClient(token_VK, user_id)
    formatted_photo = vk_client.get_formatted_photo_info(5)
    photo_info = vk_client.get_formatted_photo_info()
    create_json_file(photo_info)

    yd_client = YandexDiskAPIClient(token_yd)
    yd_client.create_folder()
    yd_client.upload_files(formatted_photo)
