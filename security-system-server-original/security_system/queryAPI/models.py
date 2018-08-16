from django.db import models


class QueryAPI(models.Model):
    code = models.CharField(max_length=50)
    msg = models.TextField()
    ids = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
