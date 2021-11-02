from django.shortcuts import render
from django.http import HttpResponse

from core import tasks

# Create your views here.

def test_req(request):
    tasks.test_function.delay()
    return HttpResponse("Done")
