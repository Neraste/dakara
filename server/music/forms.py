from django.forms import ModelForm
from music.models import *


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'
