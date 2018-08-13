from django.shortcuts import render
from django.http import HttpResponse
def index (request):

    return HttpResponse("this is a polls.index")
# Create your views here.
