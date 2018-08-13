from django.db import models


class Article(models.Model):  # 一个类就是一张表
    title = models.CharField(max_length=32)
    content = models.TextField(null=True)

    def __str__(self):
        return self.title

# Create your models here.
