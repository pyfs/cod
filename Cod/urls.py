"""Cod URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from filebrowser.sites import site
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# 系统及第三方依赖路由
urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls),
    path('mdeditor/', include('mdeditor.urls')),
    path('docs/', include('docs.urls')),
]

# 自研 APP 路由
urlpatterns += [
    path('<version>/account/', include('account.urls')),
    path('<version>/event/', include('event.urls')),
    path('<version>/project/', include('project.urls')),
    path('<version>/ds/', include('data_source.urls')),
    path('<version>/message/', include('message.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
