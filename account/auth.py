import requests
from logging import getLogger
from account.models import User
from django.contrib.auth import get_user_model
from django.http.response import HttpResponseRedirect
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.cache import cache_function
from utils.env import Env
from datetime import datetime

logger = getLogger('django')
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

env = Env()


class LoginCvte(APIView):
    """cvte oauth"""
    authentication_classes = []
    permission_classes = []

    iac_access_token = env.get('IAC_ACCESS_TOKEN')
    iac_app_id = env.get('IAC_APP_ID')
    iac_app_secret = env.get('IAC_APP_SECRET')
    op_validate_ticket = env.get('OP_VALIDATE_TICKET')
    op_app_id = env.get('OP_APP_ID')

    @cache_function('prefix', 100)
    def get_access_token(self):
        response = requests.get(url=self.iac_access_token,
                                params={'appid': self.iac_app_id, 'secret': self.iac_app_secret}).json()
        if response['status'] == 200:
            return response['data']['accessToken']
        else:
            raise Exception(response['errMsg'])

    def validate_ticket(self, ticket):
        """验证票据"""
        token = self.get_access_token()
        headers = {'x-iac-token': token}
        params = {
            'appId': self.op_app_id,
            'ticket': ticket
        }
        return requests.get(self.op_validate_ticket, headers=headers, params=params).json()

    def get(self, request, *args, **kwargs):
        ticket = request.GET.get('ticket')
        validation = self.validate_ticket(ticket=ticket)
        if validation['status'] is not '0':
            return Response({'data': validation['message']}, status=status.HTTP_400_BAD_REQUEST)

        # 获取单点登录返回的用户信息
        op_user = validation['data']['user']
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=op_user['account'])
        except User.DoesNotExist:
            return Response({'data': "用户信息找不到，请联系管理员"}, status=status.HTTP_404_NOT_FOUND)
        except User.MultipleObjectsReturned:
            return Response({'data': '用户信息重复，请联系管理员'}, status.HTTP_300_MULTIPLE_CHOICES)

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response = HttpResponseRedirect(redirect_to='/')
        if api_settings.JWT_AUTH_COOKIE:
            expiration = (datetime.utcnow() +
                          api_settings.JWT_EXPIRATION_DELTA)
            response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                token,
                                expires=expiration,
                                httponly=True)
            return response

        return HttpResponseRedirect({'data': '无论如何认证都没通过，请联系管理员'}, status=status.HTTP_400_BAD_REQUEST)
