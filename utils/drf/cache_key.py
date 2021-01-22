"""
drf-extensions cache key func
"""
from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor
from rest_framework_extensions.key_constructor import bits


class UserCacheKeyFunc(DefaultKeyConstructor):
    user = bits.UserKeyBit()  # 缓存时考虑请求用户
    params = bits.QueryParamsKeyBit()


# 必须实例化
user_cache_key_func = UserCacheKeyFunc()
