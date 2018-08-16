# -*- coding:utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^search$', views.search, name='search'),
    url(r'^protocols$', views.get_protocols, name='protocol_list'),
    url(r'^statistic/city$', views.get_statistics_by_city, name='statistics_by_city'),
]
