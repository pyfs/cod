# encoding: utf-8
# __author__ = "liushenghua"
# Date: 2021/1/28
import logging

import requests
import hmac
from hashlib import sha256
from urllib.parse import quote
from utils.env import Env

env = Env()

SHORT_APP = env.get('SHORT_APP')
SHORT_SECRET = env.get('SHORT_SECRET')
SHORT_URL = env.get('SHORT_URL')

logger = logging.getLogger('django')


class Shortener(object):
    """ 生成短网址服务"""
    def __init__(self):
        self.app_url = SHORT_URL
        self.app = SHORT_APP
        self.app_secret = SHORT_SECRET

    @staticmethod
    def create_sha256_signature(key, message):
        """ 加密消息体"""
        byte_key = key.encode("utf-8")
        message = message.encode("utf-8")
        return hmac.new(byte_key, message, digestmod=sha256).hexdigest()

    def url_to_shortener(self, url):
        """ 请求接口生成短网址"""
        payload = "longUrl=%s" % url
        signature = self.create_sha256_signature(key=self.app_secret, message=quote(payload, safe=''))
        header = {"x-auth-short-app": self.app,
                  "x-auth-short-sign": signature,
                  "Content-Type": "application/x-www-form-urlencoded"}
        data = {
            'longUrl': url
        }
        logger.info(dict(app='shortener', encode_url=quote(payload, safe='')))
        response = requests.request(method="POST", url=self.app_url, headers=header, data=data)
        if response.ok:
            result = response.json()
            logger.info(dict(app='shortener', msg=result))
            # 判断返回结果对应的节点信息
            if 'entity' in result.keys() and isinstance(result['entity'], dict):
                return result['entity']['shortUrl']
            else:
                return None
        else:
            logger.error(dict(app='shortener', msg='server no response.'))
