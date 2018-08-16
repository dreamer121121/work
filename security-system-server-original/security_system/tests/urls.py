from tests import views
from django.conf.urls import url
from django.contrib import admin

# from tests import views 

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^checkcode/$', views.check_code, name='checkcode'),
    url(r'^jsontest/', views.jsonTest),
    url(r'^login/', views.login2),
    url(r'^register/', views.register2),
    url(r'^changepwd/', views.changePwd),

    # ----------------------------------------------------
    url(r'^omg/', views.omg),
    url(r'^addUser1/', views.addUser1),
    url(r'^addUser/', views.addUser),
]
