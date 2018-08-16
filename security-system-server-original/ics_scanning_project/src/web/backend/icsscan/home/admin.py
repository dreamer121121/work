from django.contrib import admin

# Register your models here.
from home import models

admin.site.register(models.Device)
admin.site.register(models.DevicePort)
admin.site.register(models.IpLocation)
admin.site.register(models.IpPort)
admin.site.register(models.IpSubnet)
admin.site.register(models.Website)
admin.site.register(models.Protocol)