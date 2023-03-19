from urllib.parse import urljoin

import requests

from django.conf import settings


BASE_API_URL = settings.BASE_API_URL


def unauthorized_post_request(endpoint, payload):
    url = urljoin(BASE_API_URL, endpoint)
    response = requests.post(url, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None
    return response.json()


def authorized_get_request(endpoint, token, payload):
    url = urljoin(BASE_API_URL, endpoint)
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(url, headers=headers, params=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        return None
    return response.json()


def authorized_put_request(endpoint, token, payload):
    url = urljoin(BASE_API_URL, endpoint)
    headers = {'Authorization': f'Token {token}'}
    response = requests.put(url, headers=headers, json=payload)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        return None
    return response.json()


def create_user(payload):
    response_content = unauthorized_post_request('api/user/create/', payload)
    if not response_content:
        return None
    user_email = response_content.get('email')
    user_password = response_content.get('password')
    return user_email, user_password


def get_auth_token(payload):
    response_content = unauthorized_post_request('api/user/token/', payload)
    if not response_content:
        return None
    auth_token = response_content.get('token')
    return auth_token


def get_user_data(token):
    response_content = authorized_get_request('api/user/me/', token, None)
    if not response_content:
        return None
    user_email = response_content.get('email')
    user_name = response_content.get('name')
    return user_email, user_name


def get_recipes(token, params=None):
    response_content = authorized_get_request('api/recipe/recipes/', token, params)
    if not response_content:
        return None
    return response_content


def change_user_data(token, payload):
    response_content = authorized_put_request('api/user/me/', token, payload)
    if not response_content:
        return None
    user_email = response_content.get('email')
    user_name = response_content.get('name')
    return user_email, user_name
