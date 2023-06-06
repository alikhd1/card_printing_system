import json
import os

cwd = os.getcwd()
user_excel_file = os.path.join(cwd, 'users.xlsx')
settings_file = os.path.join(cwd, 'settings.conf')


def get_settings(*args):
    settings = {}
    try:
        for setting in args:
            with open(settings_file, 'r') as f:
                file = json.load(f)
                try:
                    settings[setting] = file[setting]
                except KeyError:
                    pass
    except FileNotFoundError:
        pass
    return settings


