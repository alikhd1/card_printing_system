import json


def get_settings(*args):
    settings = {}
    try:
        for setting in args:
            with open('settings.conf', 'r') as f:
                file = json.load(f)
                try:
                    settings[setting] = file[setting]
                except KeyError:
                    pass

    except FileNotFoundError:
        pass
    return settings

