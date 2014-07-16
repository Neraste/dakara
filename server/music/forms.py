from django.forms import Form, ModelForm, ValidationError, CharField, IntegerField
from django.forms.models import BaseInlineFormSet

from music.models import *

class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'

class StreamInlineFormSet(BaseInlineFormSet):
    def clean(self):
        '''Validation for streams:
            - at least one channel
            - channels all different'''
        super(StreamInlineFormSet, self).clean()
        count = 0
        channels = []
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
                    if 'channel_id' in form.cleaned_data:
                        channels.append(form.cleaned_data['channel_id'])

            except AttributeError:
                pass

        if count < 1:
            raise ValidationError('One channel needed at least')

        if len(channels) != len(set(channels)):
            raise ValidationError('Channels must be different')

class MusicSearchForm(ModelForm):
    '''Class for music search form only'''
    name = CharField(max_length = 200) 
    duration_min = IntegerField()
    duration_max = IntegerField()
    
    class Meta:
        model = Music
        fields= ('name', 'version', 'is_short', 'is_remix', 'is_cover', 'date', 'languages', 'duration_min', 'duration_max')

    def __init__(self, *args, **kwargs):
        super(MusicSearchForm, self).__init__(*args, **kwargs)
        # make all fields unrequired
        for key in self.fields:
            self.fields[key].required = False
