from django.shortcuts import render


def tos(request):
    return render(request, 'tos.html')


def index(request):
    return render(request, 'index.html')
