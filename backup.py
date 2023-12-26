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
from datetime import datetime

import requests
from tqdm import tqdm


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

# подставить токен, полученный из VK
token_VK = ''


class VKAPIClient:
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id
        self.api_base_url = 'https://api.vk.ru/method'

    def _get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }

    def get_profile_photos(self):
        """Получение фотографий профиля."""
        params_profile_photos = self._get_common_params()
        params_profile_photos.update({
            'owner_id': self.user_id,
            'album_id': 'profile',
            'extended': 1
        })
        response = requests.get(
            f'{self.api_base_url}/photos.get',
            params=params_profile_photos
        )
        data = response.json()
        if 'error' in data:
            text_error = "Token is expired, please update the token!"
            logger.error(text_error)
            raise Exception(text_error)

        return data

    def get_formatted_photo_info(self, count_saved_foto=None):
        """
        Переформатирование информации о фотографиях, полученных из VK.
        Количество выгружаемых фотографий можно ограничить параметром
        'count_saved_foto'. По умолчанию выгружаются все фотографии.
        """
        full_info_photo = self.get_profile_photos()

        count = 0
        photo_info = {}
        for info in full_info_photo['response']['items']:
            file_name = f"{info['likes']['count']}.jpg"
            if file_name in photo_info:
                date = datetime.utcfromtimestamp(info['date'])
                date = date.strftime('%Y-%m-%d')
                file_name = f"{info['likes']['count']}_{date}.jpg"

            photo_info[file_name] = {}
            photo_info[file_name]['size'] = info['sizes'][-1]['type']
            photo_info[file_name]['url'] = info['sizes'][-1]['url']

            count += 1
            if count_saved_foto is not None and count == count_saved_foto:
                break

        return photo_info

    def create_json_file(self):
        """Сохранение инфо по фотографиям в json-файл"""
        list_sizes = []
        photo_info = self.get_formatted_photo_info()
        for file_name, info in photo_info.items():
            dict_size = {'file_name': file_name, 'size': info['size']}
            list_sizes.append(dict_size)

        with open('result_info.json', 'w') as f:
            json.dump(list_sizes, f, indent=2)


class YandexDiskAPIClient:
    def __init__(self, token):
        self.token = token
        self.api_base_url = 'https://cloud-api.yandex.net'

    def _get_common_headers(self):
        return {'Authorization': f'OAuth {self.token}'}

    def create_folder(self):
        """Создание папки на ЯД."""
        url_create_folder = f'{self.api_base_url}/v1/disk/resources'
        params_create_folder = {'path': 'Photo'}
        response = requests.put(
            url_create_folder,
            params=params_create_folder,
            headers=self._get_common_headers()
        )

        if response.status_code == 201:
            logger.info('The folder has been created')
        elif response.status_code == 409:
            logger.warning('The folder already exists')
        else:
            logger.error('The folder has not been created')
            raise Exception('Error in creating a folder')

    def upload_files(self, vk_photo):
        """Скачивание файла из VK и загрузка на ЯД."""
        url_get_link = f"{self.api_base_url}/v1/disk/resources/upload"

        for file_name, info in tqdm(vk_photo.items()):
            params_load_files = {
                'url': info['url'],
                'path': f'Photo/{file_name}'
            }
            response = requests.post(
                url_get_link,
                params=params_load_files,
                headers=self._get_common_headers()
            )

            if response.status_code == 202:
                logger.info(f"The file {file_name} is uploaded")
            else:
                logger.warning(f"The file {file_name} didn't load")


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) != 3:
        raise Exception('Call the script and enter 2 arguments')

    user_id = arguments[1]
    token_yd = arguments[2]

    vk_client = VKAPIClient(token_VK, user_id)
    formatted_photo = vk_client.get_formatted_photo_info(5)
    vk_client.create_json_file()

    yd_client = YandexDiskAPIClient(token_yd)
    yd_client.create_folder()
    yd_client.upload_files(formatted_photo)
