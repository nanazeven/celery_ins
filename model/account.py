# -*- coding:utf-8 -*-

class Account():
    def __init__(self, data=None):
        self._init(data)

    def _init(self, data):
        for k, v in data.items():
            if k == 'id':
                self._id = v
            elif k == 'username':
                self._username = v
            elif k == 'full_name':
                self._full_name = v
            elif k == 'edge_followed_by':
                self._followed_by_count = v['count']
            elif k == 'edge_follow':
                self._follow_count = v['count']
            elif k == 'profile_pic_url':
                self._profile_pic_url = v
            elif k == 'profile_pic_url_hd':
                self._profile_pic_url_hd = v
            elif k == 'edge_owner_to_timeline_media':
                self._medias_count = v['count']

    @property
    def id(self):
        return self._id

    @property
    def username(self):
        return self._username

    @property
    def followed_by_count(self):
        return self._followed_by_count

    @property
    def follow_count(self):
        return self._follow_count

    @property
    def medias_count(self):
        return self._medias_count
