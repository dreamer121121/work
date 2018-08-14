from django.shortcuts import render
from django.http import Http404, HttpResponse
def hello(reauest):
    return HttpResponse("hello django")
