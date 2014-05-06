from django.contrib import messages
from django.forms.models import modelformset_factory
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from music.models import *
from music.forms import *


def multiEdit(request,Model):
    FormSet = modelformset_factory(Model) 
    if request.method == 'POST': #form has been submitted, process data
        fSet = FormSet(request.POST)
        if fSet.is_valid():
            fSet.save()
            messages.success(request, 'Data saved ^^')
            return HttpResponseRedirect(request.get_full_path() )
    else:
        fSet = FormSet()
    return render(request, 'music/multiedit.html', {'formSet': fSet})

