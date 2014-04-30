from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from music.models import *
from music.forms import *

def langIndex(request):
    langList = Language.objects.all()
    if request.method == 'POST': #form has been submitted, process data
        langForms = [LanguageForm(request.POST,instance=lang,prefix=str(lang.id)) for lang in langList]
        newLangForm  = LanguageForm(request.POST)
        if not newLangForm.is_valid():
           newLangForm = LanguageForm()

        if all([f.is_valid() for f in langForms]): #check every entry validity
            [f.save() for f in langForms]
            if newLangForm.is_valid():
                newLangForm.save()
            return HttpResponseRedirect(reverse('langIndex'))
    else:
        langForms = [LanguageForm(instance=lang,prefix=str(lang.id)) for lang in langList]
        newLangForm = LanguageForm() 
    return render(request, 'music/lang.html', {'langForms': langForms , 'newLangForm' : newLangForm})

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
