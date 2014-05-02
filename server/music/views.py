from django.forms.models import modelformset_factory
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from music.models import *
from music.forms import *

def langIndex(request):
    LanguageFormSet = modelformset_factory(Language) 
    if request.method == 'POST': #form has been submitted, process data
        langFormSet = LanguageFormSet(request.POST)
        if langFormSet.is_valid():
            langFormSet.save()
            return HttpResponseRedirect(reverse('langIndex'))
    else:
        langFormSet = LanguageFormSet()
    return render(request, 'music/lang.html', {'langFormSet': langFormSet})

def langAdd(request):
    f = LanguageForm(request.POST)
    if f.is_valid(): 
        f.save()
        return HttpResponseRedirect(reverse('langIndex'))
    else:
        return langIndex(request, "Name should not be empty")

def langDel(request,langId):
    l = get_object_or_404(Language, pk=langId)
    l.delete()
    
    return HttpResponseRedirect(reverse('langIndex'))
