from django.forms import ModelForm, Form, CharField, EmailField, PasswordInput, ValidationError

from singer.models import *

def password_validation(cleaned_data):
    '''Check password validation:
        - password1 and password2 present,
        - password1 equal to password2,
        - password1 larger than 6 characters'''
    if not ('password1' in cleaned_data and 'password2' in cleaned_data and cleaned_data['password1'] and cleaned_data['password2']):
        raise ValidationError('You must define a password')
    if cleaned_data['password1'] != cleaned_data['password2']:
        raise ValidationError('Passwords must be equal')
    if len(cleaned_data['password1']) < 6: # minimal password length check
        raise ValidationError('Password too short')

class SingerNewMinimalForm(Form):
    username = CharField(max_length = 30, label = "Login")
    email = EmailField(label = "Email address")
    password1 = CharField(max_length = 30, widget = PasswordInput(), label = "Password")
    password2 = CharField(max_length = 30, widget = PasswordInput(), label = "Retype password")
    
    def clean_username(self):
        try:
            Singer.objects.get(username__iexact = self.cleaned_data['username'])
        
        except Singer.DoesNotExist:
            return self.cleaned_data['username']

        raise ValidationError('An user with the same login already exists')

    def clean(self):
        password_validation(self.cleaned_data)

        return self.cleaned_data

    def save(self):
        new_singer = Singer.objects.create_user(
                username = self.cleaned_data['username'],
                email = self.cleaned_data['email'],
                password = self.cleaned_data['password1']
                )

        return new_singer
