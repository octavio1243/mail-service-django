import json
import requests
from decouple import config

from .token import get_user_id, get_token_permissions, set_token_permissions

allowed_permissions = ["admin"]

def check_permissions(permissions):
    global allowed_permissions

    for permission in eval(permissions):
        if permission in allowed_permissions:
            return True
    return False

def is_authenticated_and_authorized(str_token):
    user_id = get_user_id(str_token)
    if user_id:
        user_token, permissions = get_token_permissions(user_id)
        if not user_token and current(str_token):
            user_token, permissions = get_token_permissions(user_id)
        if user_token == str_token and check_permissions(permissions):
            return True
    return False

def current(str_token):
    print("Autenticando con el servicio de Auth...")
    url = f"{config('security_server')}/v1/users/current"
    headers = {
        "Authorization": str_token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        user_id = response_json["id"]
        permissions = str(response_json["permissions"])
        set_token_permissions(user_id, str_token, permissions)
        return True
    return False