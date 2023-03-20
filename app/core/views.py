from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from core import api_methods
from core.models import User, Recipe, Ingredient


def index(request):
    context = {
        'user_authorised': request.user.is_authenticated
    }
    return render(request, 'index.html', context)


def register_user(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            email=request.POST.get('email'),
            name=request.POST.get('name'),
            password=request.POST.get('password')
        )

        user = authenticate(email=user.email, password=user.password)

        if user:
            login(request, user)

        return redirect('index')
    context = {
        'mock': 'mock'
    }
    return render(request, 'registration.html', context)


def authenticate_user(request):
    if request.method == 'POST':
        user = authenticate(
            email=request.POST.get('email'), 
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('index')
        else:
            alert_message = 'Email or password is incorrect'
    context = {
        'mock': 'mock'
    }
    return render(request, 'auth.html', context)


def get_checked_allergies(request_payload):
    allergies = [
        'FISH',
        'MEAT',
        'GRAIN',
        'HONEY',
        'NUTS',
        'LACTOSE',
    ]
    checked_allergies = []
    for allergy in allergies:
        if request_payload.get(allergy):
            checked_allergies.append(allergy)    
    return checked_allergies


def get_user_allergies(user):
    allergies = [
        {'name': 'FISH', 'label': 'Рыба', 'state': None},
        {'name': 'MEAT', 'label': 'Мясо', 'state': None},
        {'name': 'GRAIN', 'label': 'Зерновые', 'state': None},
        {'name': 'HONEY', 'label': 'Мед', 'state': None},
        {'name': 'NUTS', 'label': 'Орехи', 'state': None},
        {'name': 'LACTOSE', 'label': 'Лактоза', 'state': None}
    ]
    for allergy in allergies:
        if allergy['name'] in user.allergy_type:
            allergy['state'] = 'checked'
    return allergies


def user_account(request):
    if not request.user.is_authenticated:
        return redirect('authenticate_user')
    alert_message = None
    
    if request.method == 'POST':
        if request.POST.get('email'):
            request.user.email = request.POST.get('email')
        if request.POST.get('name'):
            request.user.name = request.POST.get('name')
        if request.POST.get('password'):
            request.user.set_password(request.POST.get('password'))
        
        checked_allergies = get_checked_allergies(request.POST)
        if not set(request.user.allergy_type) == set(checked_allergies):
            request.user.allergy_type = checked_allergies

        request.user.save()
        alert_message = 'User personal data changed'

    user_email = request.user.email
    user_name = request.user.name
    allergies = get_user_allergies(request.user)
    
    context = {
        'user': {'name': user_name, 'email': user_email, 'password': '*********'},
        'allergies': allergies,
        'menu': {'name': 'menu1', 'calories': 100500, 'persons': 2, 'allergies': 'something', 'eating_times': 4},
        'alert': alert_message
    }
    return render(request, 'lk.html', context)


def logout_user(request):
    if not request.user.is_authenticated:
        return redirect('authenticate_user')
    logout(request)
    return redirect('index')


def show_recipes_cards(request):
    if not request.user.is_authenticated:
        return redirect('authenticate_user')

    recipes = list(Recipe.objects.all().prefetch_related('ingredients'))
    for recipe in recipes:
        print('Recipe:', recipe)
        recipe.ingreds = recipe.ingredients.all()
        total_calories = sum([ingredient.calories for ingredient in recipe.ingreds])
        recipe.total_calories = total_calories
        recipe.fits = True
        if set(recipe.allergy_type).intersection(set(request.user.allergy_type)):
            recipe.fits = False
    
    recipes = [recipe for recipe in recipes if recipe.fits]
    context = {
        'recipes': recipes
    }
    return render(request, 'cards.html', context)
