import requests

from dialog import show_dialog
from settings import get_settings

BASE_URL = get_settings('api_base_url')['api_base_url']


def get_user_info(param):
    url = BASE_URL + '/users/'
    if param:
        response = requests.get(url, params=param, timeout=10.0)
        if response.status_code == 200:
            result = response.json()
            return result
        if response.status_code == 404:
            show_dialog(msg='کاربری با شماره این مشخصات نشد')
