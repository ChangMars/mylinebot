"""mylinebot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from app.api.login.login import CustomLoginView
from app.api.test.test import TestViewSet
from app import views

router = DefaultRouter()#宣告使用rest_framework框架的router
router.register(r'test',TestViewSet,basename='test')

urlpatterns = [
    path('admin/', admin.site.urls),#django管理帳戶url
    path('api/v0/account/login/', CustomLoginView.as_view(), name='login'),#DRF使用權限登入url
    url(r'^app/',include('app.urls')),#自定義連接app url
    url(r'^api/v0/', include(router.urls)),#註冊router地址透過django url
    url(r'^oil_history_price_rander/',views.oil_history_price)#charts url
]
