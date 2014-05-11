from django.forms import ModelForm, ValidationError
from django.forms.models import BaseInlineFormSet
from music.models import *


class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'

class NameInlineFormSet(BaseInlineFormSet):
    '''Validation for names:
        - at least one name in name container
        - at least one main name
        - only one main name'''
    def clean(self):
        super(NameInlineFormSet, self).clean()
        # get forms that actually have valid data
        count = 0
        count_main = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
                    if 'is_main' in form.cleaned_data and form.cleaned_data['is_main']: # check number of main names
                        count_main += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise ValidationError('One name needed at least')
        if not count_main:
            raise ValidationError('One main name needed')
        if count_main > 1:
            raise ValidationError('Only one main name needed')

class StreamInlineFormSet(BaseInlineFormSet):
    '''Validation for streams:
        - at least one channel
        - channels all different'''
    def clean(self):
        super(StreamInlineFormSet, self).clean()
        count = 0
        channels = []
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
                    print form.cleaned_data
                    if 'channel_id' in form.cleaned_data:
                        channels.append(form.cleaned_data['channel_id'])

            except AttributeError:
                pass

        if count < 1:
            raise ValidationError('One channel needed at least')

        if len(channels) != len(set(channels)):
            raise ValidationError('Channels must be different')

