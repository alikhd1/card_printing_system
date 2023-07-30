import json

import requests

from dialog import show_dialog
from settings import get_settings


def get_user_info(param, many=False):
    BASE_URL = get_settings('api_base_url').get('api_base_url')
    if BASE_URL:
        url = BASE_URL + '/customers/get_sub_code/'
        if many:
            url = BASE_URL + '/customers/info/all/'
        if param:
            response = requests.get(url, params=param, timeout=10.0)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                show_dialog(msg='کاربری با شماره این مشخصات نشد')
    else:
        show_dialog(msg='آدرس API صحیح نمیباشد')


def login_almas_user(username, password):
    BASE_URL = get_settings('api_base_url').get('api_base_url')
    if BASE_URL:
        url = BASE_URL + '/users/login/'
        username = username.replace("ی", "ي")
        data = {'username': username, 'password': password}
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(url, json.dumps(data), timeout=10.0, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result
        if response.status_code == 404:
            show_dialog(msg='کاربری با این مشخصات یافت نشد')
    else:
        show_dialog(msg='آدرس API صحیح نمیباشد')
