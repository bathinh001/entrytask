from __future__ import unicode_literals
from .forms import LoginForm
from utils.utils_authentication import verify
from utils.utils_authentication import response_login
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


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
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'message': message})


