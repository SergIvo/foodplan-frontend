from django.shortcuts import render


def index(request):
    context = {
        'mock': 'mock'
    }
    return render(request, 'index.html', context)


def register_user(request):
    if request.method == 'POST':
        print(request.POST.get('name'))
    context = {
        'mock': 'mock'
    }
    return render(request, 'registration.html', context)


def authenticate_user(request):
    context = {
        'mock': 'mock'
    }
    return render(request, 'auth.html', context)


def user_account(request):
    context = {
        'user': {'name': 'random', 'email': 'something@sample.com', 'password': 'some_password'},
        'menu': {'name': 'menu1', 'calories': 100500, 'persons': 2, 'allergies': 'something', 'eating_times': 4}
    }
    return render(request, 'lk.html', context)


def show_dishes_cards(request):
    context = {
        'dishes': [
            {'name': 'something1'},
            {'name': 'something2'},
            {'name': 'something3'},
            {'name': 'something4'},
            {'name': 'something5'},
        ]
    }
    return render(request, 'card2.html', context)
