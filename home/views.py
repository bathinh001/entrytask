from __future__ import unicode_literals
from django.http import JsonResponse
import json
from jsonschema import validate
from .forms import LoginForm
from utils.utils_authentication import verify, attach_token
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from datetime import datetime, timedelta
from Event.views import create_event

TIME_EXPIRED = 5 #minutes


@csrf_exempt
def login(request):
    message = False
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            check = verify(username, password)
            if check:
                type_user = check.get('type', None)
                response = HttpResponse('Login successful', status=200)
                '''if type_user == 0:
                    response = redirect(create_event)
                    response.status_code = 301'''
                token = attach_token(username, TIME_EXPIRED)
                response.set_cookie(key='Authorization', value=token, expires=timedelta(minutes=TIME_EXPIRED)+datetime.utcnow())
                return response
            else:
                message = True
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'message': message})
