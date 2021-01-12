import abc
import json
import logging
import requests
from utils.env import Env

logger = logging.getLogger('django')
env = Env()

IAC_ACCESS_TOKEN_URL = env.get('IAC_ACCESS_TOKEN')
IAC_PUSH_API = env.get('IAC_PUSH_API')
IAC_APP_ID = env.get('IAC_APP_ID')
IAC_APP_SECRET = env.get('IAC_APP_SECRET')
USERNAME_TO_WX_ID_URL = env.get('USERNAME_TO_WX_ID_URL')
WX_WORK_ACCESS_TOKEN_URL = env.get('WX_WORK_ACCESS_TOKEN_URL')
WX_WORK_MESSAGE_POST_URL = env.get('WX_WORK_MESSAGE_POST_URL')
WX_WORK_CORP_ID = env.get('WX_WORK_CORP_ID')
WX_WORK_CORP_SECRET = env.get('WX_WORK_CORP_SECRET')
WX_APP_ID = env.get('WX_APP_ID')
NOTICE_EMAIL = env.get('NOTICE_EMAIL')
SMS_TYPE_ID = env.get('SMS_TYPE_ID')


class Alerter(object, metaclass=abc.ABCMeta):
    """告警类型基类"""

    CONTENT_TYPE = 'application/json'

    def __init__(self):
        self.iac_access_token = self.get_iac_access_token()

    @abc.abstractmethod
    def alert(self, users, content, **kwargs):
        raise NotImplementedError

    @staticmethod
    def get_info():
        return {'type': 'UnKnown'}

    @staticmethod
    def get_iac_access_token():
        """获取 ITAPI 接入token"""

        response = requests.get(url=IAC_ACCESS_TOKEN_URL, params={'appid': IAC_APP_ID, 'secret': IAC_APP_SECRET})
        json_response = response.json()
        if json_response['status'] != 200 or json_response['errCode'] != 0:
            return None
        logger.debug('token: %s' % response.text)
        return json_response['data']['accessToken']

    def form_send_user(self, users):
        """筛查无效用户"""

        full_url = '%s/%s' % (USERNAME_TO_WX_ID_URL, users)
        try:
            response = requests.get(url=full_url, headers={'access-token': self.iac_access_token}).json()
            form_user = {'username': response['data']['alias']}
        except requests.HTTPError:
            form_user = ''
            logger.error('Error: "{0}" does not exist'.format(users))
        return form_user


class WxAlerter(Alerter):
    """企业微信直通发送"""

    def __init__(self):
        super().__init__()
        self.iac_access_token = self.get_iac_access_token()
        self.wx_work_access_token = self.get_wx_work_access_token()
        self.wx_app_id = WX_APP_ID

    @staticmethod
    def get_wx_work_access_token():
        """获取企业微信接入token"""

        response = requests.get(url=WX_WORK_ACCESS_TOKEN_URL,
                                params={'corpid': WX_WORK_CORP_ID, 'corpsecret': WX_WORK_CORP_SECRET})
        json_response = response.json()
        if json_response['errcode'] != 0 or json_response['errmsg'] != 'ok':
            return None
        logger.debug('token: %s' % response.text)
        return json_response['access_token']

    def get_wx_userid(self, username):
        """域账号获取企业微信 ID, 接口暂不支持批量操作"""

        full_url = '%s/%s' % (USERNAME_TO_WX_ID_URL, username)
        try:
            response = requests.get(url=full_url, headers={'access-token': self.iac_access_token}).json()
            wx_userid = response['data']['wxId']
        except requests.HTTPError:
            wx_userid = ''
            logger.error('Error: "{0}" does not exist'.format(username))
        return wx_userid

    @staticmethod
    def get_wx_content(content):
        """获取发送内容"""
        wx_content = content
        if not wx_content:
            error_message = "WeChat Message Content Is Empty"
            logger.error(error_message)
        elif len(wx_content) > 2048:
            error_message = "WeChat Message Content Exceeds The Maximum Limit"
            logger.error(error_message)
        return wx_content

    def alert(self, users, content, **kwargs):
        """告警微信发送"""
        wx_users = []

        if isinstance(users, list):
            wx_users = '|'.join([self.get_wx_userid(user) for user in users])
        if isinstance(users, str):
            wx_users = '|'.join([self.get_wx_userid(user) for user in users.split(';')])

        try:
            headers = {
                'Content-Type': self.CONTENT_TYPE,
            }

            """
            获取text类型的 POST 数据
            @param users: 用户,以'；'分隔的字符串或列表
            @param content: 发送内容

            """
            post_data = {
                "touser": wx_users,
                "msgtype": "text",
                "agentid": self.wx_app_id,
                "text": {
                    "content": self.get_wx_content(content)
                },
                "safe": 0,
                "enable_id_trans": 0,
                "enable_duplicate_check": 0
            }
            try:
                response = requests.post(url=WX_WORK_MESSAGE_POST_URL, headers=headers,
                                         params={'access_token': self.wx_work_access_token},
                                         data=json.dumps(post_data)).json()
            except requests.HTTPError as error:
                logger.error(error)
                return {'result': False}
            if response['errmsg'] == 'ok':
                logger.info({"source": "WeCom_direct",
                             "tousers": users,
                             "result": True,
                             "message": response['errmsg'],
                             "invaliduser": response['invaliduser']})
                return {'result': True}

        except Exception as e:
            logger.error(e)

    def get_info(self):
        return {'type': 'wx_alerter'}


class ItapisWxAlerter(Alerter):
    """ITAPIS接口发送微信告警"""

    def __init__(self):
        super().__init__()
        self.itapis_wx_work_access_token = self.get_iac_access_token()
        self.wx_app_id = WX_APP_ID

    def alert(self, users, content, **kwargs):
        format_send_users = [self.form_send_user(user) for user in users]
        send_users = [user for user in format_send_users if user]  # 过滤不存在的账号

        headers = {
            'Content-Type': self.CONTENT_TYPE,
            'access-token': self.itapis_wx_work_access_token
        }

        """
        获取text类型的 POST 数据
        @param users: 用户列表
        @param content: 发送内容, 字符串格式

        """
        data = {
            'conReply': False,
            'notifyWay': '1000',
            'config': json.dumps({'wx': {'appId': self.wx_app_id, 'type': 'text'}}),
            'toUser': json.dumps(send_users),
            'content': content
        }

        try:
            response = requests.post(url=IAC_PUSH_API, headers=headers,
                                     data=json.dumps(data)).json()
        except requests.HTTPError as error:
            logger.error(error)
            return {'result': False}
        if response['message'] == 'success':
            logger.info({'source': 'WeCom',
                         'tousers': users,
                         'result': True,
                         'message': response['message'],
                         'data': response['data']})
            return {'result': True}


class EmailAlerter(Alerter):
    """邮件发送告警"""

    def __init__(self):
        super().__init__()
        self.itapis_wx_work_access_token = self.get_iac_access_token()

    def alert(self, users, content, **kwargs):
        title = kwargs.get('title')
        format_send_users = [self.form_send_user(user) for user in users]
        send_users = [user for user in format_send_users if user]  # 过滤不存在的账号

        headers = {
            'Content-Type': self.CONTENT_TYPE,
            'access-token': self.itapis_wx_work_access_token
        }

        """
        获取text类型的 POST 数据
        @param users: 用户列表
        @param content: 发送内容, 字符串格式
        @param title: 邮件标题, 字符串格式
        """
        data = {
            'conReply': False,
            'notifyWay': '0010',
            'config': json.dumps({'mail': {'mailFromName': NOTICE_EMAIL}}),
            'toUser': json.dumps(send_users),
            'title': title,
            'content': content
        }
        try:
            response = requests.post(url=IAC_PUSH_API, headers=headers,
                                     data=json.dumps(data)).json()
        except requests.HTTPError as error:
            logger.error(error)
            return {'result': False}
        if response['message'] == 'success':
            logger.info({'source': 'Email',
                         'tousers': users,
                         'result': True,
                         'message': response['message'],
                         'data': response['data']})
            return {'result': True}


class PhoneAlerter(Alerter):
    """电话告警功能"""

    def __init__(self):
        """"""
        super().__init__()
        self.itapis_wx_work_access_token = self.get_iac_access_token()
        self.sms_type_id = SMS_TYPE_ID
        self.sms_templateID = 4177

    def alert(self, users, content, **kwargs):
        print("方法调用成功，传入参数：users='%s',content='%s'" % (users, content))
        format_send_users = [self.form_send_user(user) for user in users]
        send_users = [user for user in format_send_users if user]  # 过滤不存在的账号

        headers = {
            'Content-Type': self.CONTENT_TYPE,
            'access-token': self.itapis_wx_work_access_token
        }

        """
        获取text类型的 POST 数据
        @param users: 用户列表
        @param content: 发送内容, 字符串格式
        @param title: 邮件标题, 字符串格式
        """
        data = {
            'conReply': False,
            'notifyWay': '0001',
            'config': json.dumps({'sms': {'type': self.sms_type_id, 'templateId': self.sms_templateID}}),
            'toUser': json.dumps(send_users),
            'content': content
        }
        try:
            response = requests.post(url=IAC_PUSH_API, headers=headers,
                                     data=json.dumps(data)).json()
        except requests.HTTPError as error:
            logger.error(error)
            return {'result': False}
        if response['message'] == 'success':
            logger.info({'source': 'Phone',
                         'tousers': users,
                         'result': True,
                         'message': response['message'],
                         'data': response['data']})
            return {'result': True}


class SMSAlerter(Alerter):
    """短信告警功能"""

    def __init__(self):
        """"""
        super().__init__()

    def alert(self, users, content, **kwargs):
        print("方法调用成功，传入参数：users='%s',content='%s'" % (users, content))
