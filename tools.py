# -*- coding:utf-8 -*-
from functools import reduce

BASE_URL = "https://www.instagram.com"
LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
ACCOUNT_PAGE = 'https://www.instagram.com/{}'
USER_INFO_BY_ID = 'https://i.instagram.com/api/v1/users/{}/info/'
ACCOUNT_MEDIAS = 'https://www.instagram.com/graphql/query/?query_hash=f2405b236d85e8296cf30347c9f08c2a&variables={}'
MEDIA_URL = 'https://www.instagram.com/p/{}/?__a=1'
PROXIES = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080',
    }
USERNAME = "test"
PASSWORD = 'test'
TARGET = 'test'

MONGO_URI = 'mongodb://root:root@localhost:27017'
MONGO_DB = 'instagram_data'
def get_from_dict(data_dict, map_list):
    def get_item(source, key):
        try:
            if isinstance(source, dict) and key not in source.keys():
                return None
            if isinstance(source, list):
                return source[int(key)]
            if not source:
                return None
        except:
            return None
        return source[key]

    return reduce(get_item, map_list, data_dict)
