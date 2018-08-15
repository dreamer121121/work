# -*- coding:utf-8 -*-
from django.conf.urls import url
from. import views
urlpatterns = [
    url(r'^search/$', views.search, name='search'),
    url(r'contact/$', views.contact, name='contact')
    url(r'contact_action/$', views.contact_us, name='contact_us')
]