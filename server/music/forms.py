from django.forms import ModelForm, ValidationError
from django.forms.models import BaseInlineFormSet
from music.models import *


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'

class NameInlineFormset(BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        count = 0
        countMain = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
                    if form.cleaned_data['isMain']: # check number of main names
                        countMain += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise ValidationError('One name needed at least')
        if not countMain:
            raise ValidationError('One main name needed')
        if countMain > 1:
            raise ValidationError('Only one main name needed')

