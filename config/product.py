from config.base import *

DEBUG = env.get('DEBUG', False)

# 秘钥，请妥善保存
SECRET_KEY = env.get('SECRET_KEY')

# 消息队列
CELERY_BROKER_URL = env.get('CELERY_BROKER_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.get('DB_NAME'),
        'USER': env.get('DB_USERNAME'),
        'PASSWORD': env.get('DB_PASSWORD'),
        'HOST': env.get('DB_HOST'),
        'PORT': env.get('DB_PORT'),
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.get('CACHE_REDIS_HOST'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": env.get('CACHE_REDIS_PASSWORD')
        }
    }
}
