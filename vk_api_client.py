import logging
from datetime import datetime

import requests

# логирование
logger = logging.getLogger()


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

        photo_info = {}
        for index, info in enumerate(full_info_photo['response']['items'], start=1):
            file_name = f"{info['likes']['count']}.jpg"
            if file_name in photo_info:
                date = datetime.utcfromtimestamp(info['date'])
                date = date.strftime('%Y-%m-%d')
                file_name = f"{info['likes']['count']}_{date}.jpg"

            photo_info[file_name] = {}
            photo_info[file_name]['size'] = info['sizes'][-1]['type']
            photo_info[file_name]['url'] = info['sizes'][-1]['url']

            if count_saved_foto is not None and index == count_saved_foto:
                break

        return photo_info
