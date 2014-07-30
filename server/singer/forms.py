from django import forms

from singer.models import *

def password_validation(cleaned_data):
    '''Check password validation:
        - password1 and password2 present,
        - password1 equal to password2,
        - password1 larger than 6 characters'''
    if not ('password1' in cleaned_data and 'password2' in cleaned_data and cleaned_data['password1'] and cleaned_data['password2']):
        raise forms.ValidationError('You must define a password')

    if cleaned_data['password1'] != cleaned_data['password2']:
        raise forms.ValidationError('Passwords must be equal')

    if len(cleaned_data['password1']) < 6: # minimal password length check
        raise forms.ValidationError('Password too short')

def email_validation(cleaned_data):
    '''Check if email submitted is valid:
        - doesn't already exist'''
    try:
        Singer.objects.get(email__iexact = cleaned_data['email'])
    
    except Singer.DoesNotExist:
        return cleaned_data['email']

    raise forms.ValidationError('An user with the same email already exists, please select another one')

class SingerMinimalCreationForm(forms.ModelForm):
    '''Create a singer account with minimal features (i.e. no person/name)'''
    password1 = forms.CharField(widget = forms.PasswordInput(), label = "Password")
    password2 = forms.CharField(widget = forms.PasswordInput(), label = "Password confirmation")

    class Meta:
        model = Singer
        fields = ('email',)

    def clean_email(self):
        email_validation(self.cleaned_data)

        return self.cleaned_data['email']

    def clean(self):
        password_validation(self.cleaned_data)

        return self.cleaned_data

    def save(self, commit = True):
        user = super(SingerMinimalCreationForm, self).save(commit = False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()

        return user

class SingerChangeForm(forms.ModelForm):
    '''Change a singer account'''
    class Meta:
        model = Singer
        fields = ('email', 'is_active', 'is_staff', 'is_admin')

    def clean_email(self):
        email_validation(self.cleaned_data)

        return self.cleaned_data['email']
