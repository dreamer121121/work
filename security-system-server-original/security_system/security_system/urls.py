from django.conf.urls import url, include

from monitor_system import views as monitor

urlpatterns = [
    url(r'^api/get/monitorInfo/$', monitor.getMonitorInfo),
    url(r'^', include('queryAPI.urls')),
    url(r'^online/', include('log_sys.urls')),
    url(r'^online1/', include('tests.urls')),
]
