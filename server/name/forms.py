from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from name.models import *

class NameInlineFormSet(BaseInlineFormSet):
    '''Class for person names and item names'''
    def clean(self):
        '''Validation for names:
            - at least one name in name container
            - at least one main name
            - only one main name'''
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
                    if 'is_main' in form.cleaned_data and 'DELETE' in form.cleaned_data and form.cleaned_data['is_main'] and form.cleaned_data['DELETE']:
                        raise ValidationError('Cannot delete main name')
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
