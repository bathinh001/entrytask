from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=30)
    password = forms.CharField(label='password', widget=forms.PasswordInput)


class CreateEventForm(forms.Form):
    start_date = forms.IntegerField(label='start_date')
    end_date = forms.IntegerField(label='end_date')
    name = forms.CharField(label='name')
    description = forms.CharField(label='description', max_length=1000)
    location = forms.CharField(label='location', max_length=100)
    status = forms.IntegerField(label='status')
    channel = forms.CharField(label='channel', max_length=100)

class CreateUserForm(forms.Form):
    username = forms.CharField(label='username', max_length=30)
    password = forms.CharField(label='password', widget=forms.PasswordInput)
    fullname = forms.CharField(label='fullname', max_length=50)
