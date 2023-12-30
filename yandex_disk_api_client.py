import logging

import requests
from tqdm import tqdm

# логирование
logger = logging.getLogger()


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
