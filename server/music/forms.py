from django.forms import ModelForm
from django import forms
from music.models import *


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'

class NameInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        count = 0
        countMain = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
                    if form.cleaned_data['isMain']:
                        countMain += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError('You must have at least one name')
        if not countMain:
            raise forms.ValidationError('One main name needed')
        if countMain > 1:
            raise forms.ValidationError('Only one main name needed')
