from __future__ import unicode_literals
from .forms import LoginForm
from .forms import CreateUserForm
from utils.utils_authentication import verify
from utils.utils_authentication import response_login
from utils.utils_database import is_existed
from utils.utils_database import create_user_from_data
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import HttpResponse


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
                return response_login(username)
            else:
                message = True
    '''
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'message': message})
    '''
    return HttpResponse('Hello', status=200)

@csrf_exempt
def signup(request):
    message = False
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            check = is_existed(username)
            if not check:
                create_user_from_data(form)
            else:
                message = True
    else:
        form = CreateUserForm()
    return render(request, 'signup.html', {'form': form, 'message': message})
