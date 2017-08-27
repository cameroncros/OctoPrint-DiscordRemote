#coding: utf-8

import json
import requests


class Hook():

    def __init__(self, url, message, username="", avatar="", attachment=None):
        self.url = url
        self.message = message
        self.username = username
        self.avatar = avatar
        self.attachment = attachment
        self.payload = {}

    def format(self):
        self.payload = {
            'content': self.message,
            'username' : self.username,
            'avatar_url' : self.avatar
        }

    def post(self):
        self.format()

        resp = requests.post(self.url,files=self.attachment,data=self.payload)
        if resp:
            return True
        else:
            raise Exception("Error on post : " + str(resp))