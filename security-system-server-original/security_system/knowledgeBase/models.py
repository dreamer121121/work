# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class vendor(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    country = models.CharField(max_length=255, null=True)
    url = models.CharField(max_length=255, null=True)


class VulnerabilityDevice(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    vendor = models.CharField(max_length=255, null=True)
    deviceType = models.CharField(max_length=255, null=True)


class instance(models.Model):
    """
    设备表
    """
    name = models.CharField(max_length=255, primary_key=True)
    vendor = models.CharField(max_length=255, null=True, verbose_name='厂商')
    ip = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    continent = models.CharField(max_length=255, null=True, verbose_name='洲')
    asn = models.CharField(max_length=255, null=True)
    lat = models.CharField(max_length=255, null=True, verbose_name='纬度')
    lon = models.CharField(max_length=255, null=True, verbose_name='经度')
    hostname = models.CharField(max_length=255, null=True)
    service = models.CharField(max_length=255, null=True)
    os = models.CharField(max_length=255, null=True, verbose_name='操作系统类型')
    app = models.CharField(max_length=255, null=True)
    extrainfo = models.CharField(max_length=255, null=True)
    version = models.CharField(max_length=255, null=True)
    timestamp = models.CharField(max_length=255, null=True, verbose_name='首次添加时间')
    type_index = models.CharField(max_length=255, null=True)
    organization = models.CharField(max_length=30, blank=True, null=True)
    isp = models.CharField(max_length=30, blank=True, null=True)
    update_time = models.DateTimeField(verbose_name='最后更新时间', null=True)
    from_scan = models.IntegerField(blank=True, null=True, verbose_name='来自扫描')  # 0 -> False, 1 -> True
    from_spider = models.IntegerField(blank=True, null=True, verbose_name='来自爬虫')  # 0 -> False, 1 -> True
    from_web = models.CharField(max_length=100, blank=True, null=True, verbose_name='爬虫自哪个网址')


class InstancePort(models.Model):
    """
    设备端口表
    """
    id = models.CharField(primary_key=True, max_length=36)
    ip = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    nw_proto = models.CharField(max_length=30, blank=True, null=True)  # 网络层协议, 例如TCP, UDP
    protocol = models.CharField(max_length=30, blank=True, null=True)  # 应用层协议名称, 例如Modbus
    banner = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    add_time = models.CharField(max_length=255)
    update_time = models.DateTimeField()
    instance_id = models.CharField(max_length=255, blank=True, null=True)  # 设备表ID


class IpSubnet(models.Model):
    """
    IP地址段表，用于扫描
    """
    city = models.CharField(max_length=50)  # 城市名称
    province = models.CharField(max_length=30, blank=True, null=True)  # 省
    country = models.CharField(max_length=30, blank=True, null=True)  # 国家
    ip_subnet_from = models.CharField(max_length=15)
    ip_subnet_to = models.CharField(max_length=15)


class Protocol(models.Model):
    """
    协议表
    """
    proto_name = models.CharField(max_length=30)
    nw_proto = models.CharField(max_length=30)
    port = models.IntegerField()


class IpLocation(models.Model):
    """
    IP经纬度表
    """
    ip = models.CharField(primary_key=True, max_length=15)
    lat = models.CharField(max_length=15)
    lng = models.CharField(max_length=15)
    timezone = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    organization = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=50, null=True, blank=True)
    as_num = models.CharField(max_length=50, null=True, blank=True, verbose_name="AS号")
    as_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="AS名称")
    bgp_prefix = models.CharField(max_length=50, null=True, blank=True, verbose_name="BGP前缀")


class Website(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    ip = models.CharField(max_length=15)
    port = models.IntegerField()
    lat = models.CharField(max_length=15, blank=True, null=True)
    lng = models.CharField(max_length=15, blank=True, null=True)
    asn = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    html = models.TextField(blank=True, null=True)
    header = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    add_time = models.DateTimeField()
    update_time = models.DateTimeField()

    class Meta:
        unique_together = (('ip', 'port'),)


class vulnerability(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    vendor = models.CharField(max_length=255, null=True)
    level = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=1024, null=True)
    url = models.CharField(max_length=255, null=True)
    mitigation = models.CharField(max_length=255, null=True)
    provider = models.CharField(max_length=255, null=True)
    date = models.CharField(max_length=255, null=True)


class dev2vul(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    device = models.CharField(max_length=255)
    vulnerability = models.CharField(max_length=255)
