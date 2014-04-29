from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from music.models import *
from music.forms import *

def langIndex(request, error = None):
    langList = Language.objects.all()
    
    langForms = {}
    for lang in langList:
        langForms[lang.id] = LanguageForm(instance=lang)
    
    form = LanguageForm()
    return render(request, 'music/lang.html', {'langForms': langForms,'form':form, 'error_message': error })

def langAdd(request):
    f = LanguageForm(request.POST)
    if f.is_valid(): 
        f.save()
        return HttpResponseRedirect(reverse('langIndex'))
    else:
        return langIndex(request, "Name should not be empty")

def langEdit(request,langId):
    l = get_object_or_404(Language, pk=langId)
    f = LanguageForm(request.POST,instance=l)
    if f.is_valid(): 
        f.save()
        return HttpResponseRedirect(reverse('langIndex'))
    else:
        return langIndex(request, "Name should not be empty")

def langDel(request,langId):
    l = get_object_or_404(Language, pk=langId)
    l.delete()
    
    return HttpResponseRedirect(reverse('langIndex'))
