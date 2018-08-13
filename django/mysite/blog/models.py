from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=32)
    content = models.TextField(null=True)
# Create your models here.
