# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Device(models.Model):
    ip_address = models.CharField(primary_key=True, max_length=15)
    lat = models.CharField(max_length=15, blank=True, null=True)
    lng = models.CharField(max_length=15, blank=True, null=True)
    asn = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    organization = models.CharField(max_length=30, blank=True, null=True)
    isp = models.CharField(db_column='ISP', max_length=30, blank=True, null=True)  # Field name made lowercase.
    dev_type = models.CharField(max_length=30, blank=True, null=True)
    brand = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    add_time = models.DateTimeField()
    update_time = models.DateTimeField()
    access = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 't_device'

    def __str__(self):
        return 'ip: %s, lat: %s, lng: %s, country: %s, city: %s, status: %s, add_time: %s, update_time: %s' % (
            self.ip_address, self.lat, self.lng, self.country, self.city, self.status, self.add_time, self.update_time)


# Django don't allow the PK contains two fields,
# so create an id field to be logic PK. The SQL is:
# alter table t_device_port add column id int not null;
# set @r:=0;
# update t_device_port set id=(@r:=@r+1);
# alter table t_device_port modify column id int not null unique;

# ALTER TABLE `ics_scanning`.`t_device_port` CHANGE COLUMN `id` `id` VARCHAR(36) NOT NULL ;


class DevicePort(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    ip_address = models.CharField(max_length=15)
    port = models.IntegerField()
    protocol = models.CharField(max_length=30, blank=True, null=True)
    banner = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, null=True)
    add_time = models.DateTimeField()
    update_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 't_device_port'
        unique_together = (('ip_address', 'port'),)

    def __str__(self):
        return 'ip: %s, port: %s, protocol: %s, banner: %s, status: %s, add_time: %s, update_time: %s' % (
            self.ip_address, self.port, self.protocol, self.banner, self.status, self.add_time, self.update_time)


class IpLocation(models.Model):
    ip_address = models.CharField(primary_key=True, max_length=15)
    lat = models.CharField(max_length=15)
    lng = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 't_ip_location'

    def __str__(self):
        return 'ip: %s, lat: %s, lng: %s' % (
            self.ip_address, self.lat, self.lng)


# alter table t_ip_port add column id int not null;
# set @r:=0;
# update t_ip_port set id=(@r:=@r+1);
# alter table t_ip_port modify column id int not null unique;

# ALTER TABLE `ics_scanning`.`t_ip_port` CHANGE COLUMN `id` `id` VARCHAR(36) NOT NULL ;


class IpPort(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    ip_address = models.CharField(max_length=15)
    port = models.IntegerField()

    class Meta:
        managed = False
        db_table = 't_ip_port'
        unique_together = (('ip_address', 'port'),)

    def __str__(self):
        return 'ip: %s, port: %s' % (
            self.ip_address, self.port)


class IpSubnet(models.Model):
    city = models.CharField(max_length=50)
    ip_subnet_from = models.CharField(max_length=15)
    ip_subnet_to = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 't_ip_subnet'

    def __str__(self):
        return 'city: %s, ip_subnet_from: %s, ip_subnet_to: %s' % (
            self.city, self.ip_subnet_from, self.ip_subnet_to)


# alter table t_web add column id int not null;
# set @r:=0;
# update t_web set id=(@r:=@r+1);
# alter table t_web modify column id int not null unique;

# ALTER TABLE `ics_scanning`.`t_web` CHANGE COLUMN `id` `id` VARCHAR(36) NOT NULL ;


class Website(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    ip_address = models.CharField(max_length=15)
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
        managed = False
        db_table = 't_web'
        unique_together = (('ip_address', 'port'),)

    def __str__(self):
        return 'ip: %s, header: %s, lat: %s, lng: %s, country: %s, city: %s, status: %s, add_time: %s, update_time: %s' % (
            self.ip_address, self.header, self.lat, self.lng, self.country, self.city, self.status, self.add_time,
            self.update_time)


class Protocol(models.Model):
    proto_name = models.CharField(max_length=30)
    nw_proto = models.CharField(max_length=30)
    port = models.IntegerField()

    class Meta:
        db_table = 't_protocol'

    def __str__(self):
        return 'proto_name: %s, nw_proto: %s, port: %s' % (
            self.proto_name, self.nw_proto, self.port)
