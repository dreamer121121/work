from django.shortcuts import render

from . import models


def index(request, article_id):
    if str(article_id) == '0':
        articles = models.Article.objects.all()  # 从后台（数据库）中获取文章列表
        return render(request, "blog/index.html", {'articles': articles})  # 将后台数据传递到前端
    else:
        models.Article.objects.get(id=article_id).delete()  # 从数据库中删除数据
        articles = models.Article.objects.all()  # 从后台（数据库）中获取文章列表
        return render(request, "blog/index.html", {'articles': articles})  # 将后台数据传递到前端


def article_page(request, article_id):
    article = models.Article.objects.get(pk=article_id)  # 从数据库中获取文章
    return render(request, 'blog/article_page.html', {'article': article})


def edit_page(request, article_id):
    if str(article_id) == '0':
        return render(request, 'blog/edit_page.html')
    else:
        article = models.Article.objects.get(pk=article_id)  # 获取文章
        return render(request, 'blog/edit_page.html', {'article': article})


def edit_action(request, article_id):
    if str(article_id) == '0':
        title = request.POST.get('title', 'TITLE')
        content = request.POST.get('content', 'CONTENT')
        models.Article.objects.create(title=title, content=content)  # 存入数据添加一篇新文章
        articles = models.Article.objects.all()  # 从后台（数据库）中获取文章列表
        return render(request, "blog/index.html", {'articles': articles})  # 将后台数据传递到前端
    else:
        article=models.Article.objects.get(pk=article_id)
        article.title = request.POST.get('title', 'TITLE')
        article.content = request.POST.get('content', 'CONTENT')
        article.save()  # 更新数据库
        articles = models.Article.objects.all()  # 从后台（数据库）中获取文章列表
        return render(request, "blog/index.html", {'articles': articles})  # 将后台数据传递到前端
