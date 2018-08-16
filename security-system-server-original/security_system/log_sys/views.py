# coding=utf-8
# from django.shortcuts import render
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from log_sys.models import User


# ??
class UserForm(forms.Form):
    username = forms.CharField(label='???', max_length=100)
    password = forms.CharField(label='??', widget=forms.PasswordInput())


# ??
def regist(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            # ??????
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # ??????
            User.objects.create(username=username, password=password)
            return HttpResponse('regist success!!')
    else:
        uf = UserForm()
    return render_to_response('regist.html', {'uf': uf}, context_instance=RequestContext(req))


# ??
def login(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            # ????????
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            # ???????????????
            user = User.objects.filter(username__exact=username, password__exact=password)
            if user:
                # ????,??index
                response = HttpResponseRedirect('/online/index/')
                # ?username?????cookie,?????3600
                response.set_cookie('username', username, 3600)
                return response
            else:
                # ????,??login
                return HttpResponseRedirect('/online/login/')
    else:
        uf = UserForm()
    return render_to_response('login.html', {'uf': uf}, context_instance=RequestContext(req))


# ????
def index(req):
    username = req.COOKIES.get('username', '')
    return render_to_response('index.html', {'username': username}, context_instance=RequestContext(req))


# ??
def logout(req):
    response = HttpResponse('logout !!')
    # ??cookie???username
    response.delete_cookie('username')
    return response
