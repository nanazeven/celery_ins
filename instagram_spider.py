# -*- coding:utf-8 -*-
import requests
import re
import os
import json
import pymongo
import tools
from urllib import parse
from model.account import Account
from model.media import Media


class InstagramSpider():
    def __init__(self, username, password):
        self.db = pymongo.MongoClient(tools.MONGO_URI)[tools.MONGO_DB]
        self.__req = requests.session()
        self.__user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        self.__user_session = {}
        self.__proxies = None
        self.username = username
        self.password = password
        self.__session_file_path = './session_cache'
        if not os.path.exists(self.__session_file_path):
            open(self.__session_file_path, 'a').close()
            with open(self.__session_file_path, 'w') as f:
                f.write(json.dumps({}))

    @property
    def proxies(self):
        return self.__proxies

    @proxies.setter
    def proxies(self, proxy):
        if proxy and isinstance(proxy, dict):
            self.__proxies = proxy
            self.__req.proxies = proxy

    @proxies.deleter
    def proxies(self):
        self.__proxies = None
        self.__req.proxies = {}

    @property
    def session_file(self):
        with open(self.__session_file_path, 'r') as f:
            session_file_dict = json.loads(f.read())
        if not session_file_dict:
            return None
        return session_file_dict['v']

    @session_file.setter
    def session_file(self, session):
        with open(self.__session_file_path, 'w') as f:
            full_dict = {'k': self.username, 'v': session}
            f.write(json.dumps(full_dict))

    @session_file.deleter
    def session_file(self):
        with open(self.__session_file_path, 'w') as f:
            f.write(json.dumps({}))

    def generate_header(self):
        header = {
            'User-Agent': self.__user_agent
        }
        cookies = ''
        for k, v in self.__user_session.items():
            cookies += f'{k}={v};'
        header['cookie'] = cookies
        header['referer'] = tools.BASE_URL + '/'
        return header

    def is_login(self):
        session = self.session_file
        if not session or 'sessionid' not in session:
            return False
        session_id = session['sessionid']
        csrf_token = session['csrftoken']
        header = {
            'cookie': "csrftoken=" + csrf_token + "; sessionid=" + session_id + ";",
            'referer': tools.BASE_URL + '/',
            'x-csrftoken': csrf_token,
            'x-CSRFToken': csrf_token,
            'user-agent': self.__user_agent
        }
        resp = self.__req.get(tools.BASE_URL, headers=header)
        if resp.status_code != 200:
            return False
        cookies = self.get_cookies(resp)
        if 'ds_user_id' not in cookies:
            return False
        return True

    def login(self):
        if not self.is_login():
            resp = self.__req.get(tools.BASE_URL)
            if resp.status_code != 200:
                return
            csrf_token = ''
            res = re.search(r'"csrf_token":"(.*?)"', resp.text)
            if res and res.group(1):
                csrf_token = res.group(1)
            cookies = self.get_cookies(resp)
            mid = cookies['mid']
            header = {
                'cookie': "csrftoken=" + csrf_token + "; mid=" + mid + ";",
                'referer': tools.BASE_URL + '/',
                'x-csrftoken': csrf_token,
                'user-agent': self.__user_agent
            }
            resp = self.__req.post(tools.LOGIN_URL, headers=header,
                                   data={'username': self.username, 'password': self.password})
            json_res = None
            if resp.status_code != 200:
                return
            if not re.search('<html', resp.text) and re.match(r'{.*}', resp.text):
                json_res = json.loads(resp.text)
            if 'authenticated' in json_res and not json_res['authenticated']:
                return '登陆失败'

            cookies = self.get_cookies(resp)
            cookies['mid'] = mid
            self.session_file = cookies
            self.__user_session = cookies
        else:
            self.__user_session = self.session_file

    def get_account(self, username):
        url = tools.ACCOUNT_PAGE.format(username)
        resp = self.__req.get(url, headers=self.generate_header())
        if resp.status_code != 200:
            return None
        regx = r"\s*.*\s*<script.*?>.*_sharedData\s*=\s*(.*?);<\/script>"
        match_result = re.match(regx, resp.text, re.S)
        if match_result:
            data = json.loads(match_result.group(1))
            # with open('./test.json', 'a') as f:
            #     f.write(json.dumps(data))
            account_data = tools.get_from_dict(data, ['entry_data', 'ProfilePage', 0, 'graphql', 'user'])
            if not account_data:
                return None
            account = Account(account_data)
            return account

    def get_medias(self, username, count=50):
        self.login()
        account = self.get_account(username)
        has_next_page = True
        after = ''
        medias = []
        while has_next_page:
            variables = json.dumps({
                'id': str(account.id),
                'first': count,
                'after': after
            }, separators=(',', ':'))
            url = tools.ACCOUNT_MEDIAS.format(parse.quote(variables))
            resp = self.__req.get(url, headers=self.generate_header())
            if resp.status_code != 200:
                return
            media_dict = json.loads(resp.text)
            media_raw = tools.get_from_dict(media_dict, ['data', 'user', 'edge_owner_to_timeline_media'])
            if not media_raw:
                return medias
            for temp in media_raw['edges']:
                medias.append(Media(temp['node']))
            after = media_raw['page_info']['end_cursor']
            has_next_page = media_raw['page_info']['has_next_page']
        self.update(username, medias)
        return medias

    def get_cookies(self, resp):
        cookies = resp.cookies.get_dict()
        if 'csrftoken' in cookies:
            self.__user_session['csrftoken'] = cookies['csrftoken']
        return cookies

    def update(self, collection, data):
        c = self.db[collection]
        for item in data:
            item = item.__dict__
            option = {
                'filter': {"id": item['id']},
                "update": {"$set": item},
                "upsert": True
            }
            result = c.update_one(**option)
            print(result.matched_count,result.modified_count)



