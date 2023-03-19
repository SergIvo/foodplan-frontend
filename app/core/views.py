from django.shortcuts import render, redirect
from core import api_methods


def index(request):
    print(request.session.keys())
    context = {
        'access_token': request.session.get('api_access_token')
    }
    return render(request, 'index.html', context)


def register_user(request):
    if request.method == 'POST':
        payload = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password')
        }
        email, password = api_methods.create_user(payload)

        user_token = api_methods.get_auth_token(
            {
                'email': email,
                'password': password
            }
        )
        request.session['api_access_token'] = user_token

        return redirect('index')
    context = {
        'mock': 'mock'
    }
    return render(request, 'registration.html', context)


def authenticate_user(request):
    if request.method == 'POST':
        payload = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password')
        }
        user_token = api_methods.get_auth_token(payload)
        request.session['api_access_token'] = user_token

        return redirect('index')
    context = {
        'mock': 'mock'
    }
    return render(request, 'auth.html', context)


def check_allergies(request_payload):
    allergies = [
        {'name': 'fish', 'label': 'Рыба', 'state': None},
        {'name': 'meat', 'label': 'Мясо', 'state': None},
        {'name': 'grain', 'label': 'Зерновые', 'state': None},
        {'name': 'honey', 'label': 'Мед', 'state': None},
        {'name': 'nuts', 'label': 'Орехи', 'state': None},
        {'name': 'lactose', 'label': 'Лактоза', 'state': None}
    ]
    for allergie in allergies:
        allergie['state'] = request_payload.get(allergie['name'])
    
    return allergies


def user_account(request):
    if not request.session.get('api_access_token'):
        return redirect('authenticate_user')
    api_access_token = request.session.get('api_access_token')
    user_email, user_name = api_methods.get_user_data(api_access_token)
    alert_message = None
    
    if request.method == 'POST':
        payload = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'name': request.POST.get('name')
        }
        if not payload['email']:
            payload['email'] = user_email
        if not payload['name']:
            payload['name'] = user_name
        if payload['password']:
            user_email, user_name = api_methods.change_user_data(api_access_token, payload)
            alert_message = 'User personal data changed'
        else:
            alert_message = 'Password is required for changing user data'
    
    allergies = check_allergies(request.POST)
    
    context = {
        'user': {'name': user_name, 'email': user_email, 'password': 'some_password'},
        'allergies': allergies,
        'menu': {'name': 'menu1', 'calories': 100500, 'persons': 2, 'allergies': 'something', 'eating_times': 4},
        'alert': alert_message
    }
    return render(request, 'lk.html', context)


def logout_user(request):
    if not request.session.get('api_access_token'):
        return redirect('authenticate_user')
    request.session.pop('api_access_token')
    return redirect('index')


def show_recipes_cards(request):
    if not request.session.get('api_access_token'):
        return redirect('authenticate_user')
        
    api_access_token = request.session.get('api_access_token')
    recipes = api_methods.get_recipes(api_access_token)
    for recipe in recipes:
        print('Recipe:', recipe)
        total_calories = sum([ingredient['calories'] for ingredient in recipe['ingredients']])
        recipe['total_calories'] = total_calories
    
    context = {
        'recipes': recipes
    }
    return render(request, 'cards.html', context)
