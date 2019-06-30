# -*- coding:utf-8 -*-
import json

class Media():
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_SIDECAR = 'sidecar'
    TYPE_CAROUSEL = 'carousel'

    def __init__(self, data=None):
        self.id = data['id']
        self.owner_id = data['owner']['id']
        self.owner_name = data['owner']['username']
        self.shortcode = data['shortcode']
        self.comment_count = data['edge_media_to_comment']['count']
        self.create_timestamp = data['taken_at_timestamp']
        self.like_count = data['edge_media_preview_like']['count']
        self.caption = []
        self.type = None
        self.display_url = []
        self.video_url = []
        self._init(data)

    def _init(self, data):
        for d in data['edge_media_to_caption']['edges']:
            self.caption.append(d['node']['text'])
        if data['__typename'] == 'GraphSidecar':
            self.type = self.TYPE_SIDECAR
            for d in data['edge_sidecar_to_children']['edges']:
                if d['node']['__typename'] == "GraphImage":
                    self.display_url.append(d['node']['display_url'])
                elif d['node']['__typename'] == "GraphVideo":
                    self.video_url.append(d['node']['video_url'])
        elif data['__typename'] == 'GraphImage':
            self.type = self.TYPE_IMAGE
            self.display_url.append(data['display_url'])
        elif data['__typename'] == 'GraphVideo':
            self.type = self.TYPE_VIDEO
            self.video_url.append(data['video_url'])

    def dump(self):
        return json.dumps(self.__dict__)
