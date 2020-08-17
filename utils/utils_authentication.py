import hashlib
from Database.models import UserTab
import jwt
import json
from jsonschema import validate
from datetime import datetime, timedelta
from django.core.cache import cache
from django import forms
from django.http import JsonResponse

SECRET_KEY = '^gph2f8zqdsb-rog*a4lj=1k%5afio5vw_i4uvl683(^$r!u(9'
ALGORITHM='HS512'


def verify(username, password):
    hash_pw = str(hashlib.sha512(password).hexdigest())
    cache_key = username
    stored_pw = cache.get(cache_key, None)
    if not stored_pw:
        try:
            data = UserTab.objects.values('type', 'password').get(username=username)
        except:
            return None
        stored_pw = data.get('password', None)
    if not stored_pw or hash_pw[:100] != stored_pw:
        return None
    cache.set(cache_key, stored_pw)
    return {username: stored_pw}
##################################################################################################


def create_access_token(data, expires_delta):
    expire = datetime.utcnow() + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
##################################################################################################


def attach_token(username, minutes=2):
    user_id, type = list(UserTab.objects.values_list('user_id', 'type').filter(username=username))[0]
    data = {'user_id': user_id, "type": type}
    token = create_access_token(data, timedelta(minutes=minutes))
    return token
##################################################################################################


PREFIX = 'Bearer '

'''
def get_token(header):
    if not header.startswith(PREFIX):
        return None
    return header[len(PREFIX):]
'''
##################################################################################################


def extract_token(request):
    token = request.COOKIES.get('Authorization', None)
    #headers_token = request.META.items()[0][1]
    return token
##################################################################################################


def decode_token(token):
    if token:
        return jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
    return None
##################################################################################################


def is_valid_data(data):
    try:
        data_json = json.loads(json.dumps(data))
    except:
        return False
    return True
##################################################################################################


def authorization(request):
    res = {'status': 401, "message": "Client expired or invalid"}
    try:
        data = decode_token(extract_token(request))
    except:
        return res
    data = decode_token(extract_token(request))
    if not data or not is_valid_data(data):
        return res
    schema = {
        "type": "object",
        "description": "Structure of a header request extracted from access token",
        "properties": {
            "user_id": {
                "description": "The unique identifier for user",
                "type": "number",
                "exclusiveMinimum": 0
            },
            "exp": {
                "type": "number",
                "exclusiveMinimum": 0
            },
            "type": {
                "type": "number",
                "minimum": 0
            },
        },
        "maxProperties": 3,
        "minProperties": 3,
        "required": ["user_id", "exp", "type"],
    }

    # validate the request body
    try:
        validate(instance=json.loads(json.dumps(data)), schema=schema)
    except:
        res['message'] = "invalid_request"
        return res
    user_id = data.get('user_id', None)
    exp_time = data.get('exp', None)
    type = data.get('type', None)

    res['status'] = 200
    res['message'] = "success"
    res['user_id'] = user_id
    res['exp_time'] = exp_time
    res['type'] = type
    return res
##################################################################################################

TIME_EXPIRED = 360
def response_login(username):
    res = {'message': 'Login successfully'}
    response = JsonResponse(res, status=200)
    token = attach_token(username, TIME_EXPIRED)
    response.set_cookie(key='Authorization', value=token, expires=timedelta(minutes=TIME_EXPIRED)+datetime.utcnow())
    return response
