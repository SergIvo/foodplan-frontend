from django.shortcuts import render


def index(request):
    context = {
        'mock': 'mock'
    }
    return render(request, 'index.html', context)


def register_user(request):
    context = {
        'mock': 'mock'
    }
    return render(request, 'registration.html', context)


def authenticate_user(request):
    context = {
        'mock': 'mock'
    }
    return render(request, 'auth.html', context)
