import json

import requests

from dialog import show_dialog
from settings import get_settings


def get_user_info(param):
    BASE_URL = get_settings('api_base_url')['api_base_url']
    url = BASE_URL + '/users/'
    if param:
        response = requests.get(url, params=param, timeout=10.0)
        if response.status_code == 200:
            result = response.json()
            return result
        if response.status_code == 404:
            show_dialog(msg='کاربری با شماره این مشخصات نشد')


def login_almas_user(username, password):
    BASE_URL = get_settings('api_base_url').get('api_base_url', '')
    url = BASE_URL + '/login/'
    data = {'username': username, 'password': password}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    response = requests.post(url, json.dumps(data), timeout=10.0, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result
    if response.status_code == 404:
        show_dialog(msg='کاربری با این مشخصات یافت نشد')


