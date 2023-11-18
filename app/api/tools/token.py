from django.core.cache import cache
import json
import base64

def get_user_id(token):
    if not token:
        return None
    jwt_token = token.split(" ")[1]
    header, body, signature = jwt_token.split(".")
    decoded_body = base64.urlsafe_b64decode(body + "===")
    body_str = decoded_body.decode("utf-8")
    user_id = json.loads(body_str)["userID"]
    return user_id

def get_token_permissions(user_id):
    token_permissions = cache.get(f'user_token_permissions_{user_id}')
    if not token_permissions:
        return None, None
    return token_permissions.split(":")

def set_token_permissions(user_id, token, permissions):
    token_permissions = f'{token}:{permissions}'
    cache.set(f'user_token_permissions_{user_id}', token_permissions)
    
def delete_token_permissions(user_id):
    cache.delete(f'user_token_permissions_{user_id}')

