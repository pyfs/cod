from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'utils.drf.pagination.CommonPageNumberPagination',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions'
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
    'VERSION_PARAM': 'version',
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(days=30),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'account.utils.jwt_response_payload_handler',
    'JWT_AUTH_COOKIE': 'JWT'
}

# drf-extensions settings
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 5,
    'DEFAULT_CACHE_KEY_FUNC': 'utils.drf.cache_key.user_cache_key_func',
}
