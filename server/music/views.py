from django.contrib import messages
from django.forms.models import modelformset_factory
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from music.models import *
from music.forms import *

from utils import get_related

def multi_edit(request,Model):
    FormSet = modelformset_factory(Model) 
    if request.method == 'POST': #form has been submitted, process data
        f_set = FormSet(request.POST)
        if f_set.is_valid():
            f_set.save()
            messages.success(request, 'Data saved ^^')
            return HttpResponseRedirect(request.get_full_path() )
        else:
            messages.error(request, "Error in fields :(")
    else:
        f_set = FormSet()
    return render(request, 'music/multiedit.html', {'formSet': f_set})

def multi_delete(request, id, Model):
    obj = get_object_or_404(Model,pk=id)
    if request.method == 'POST': #form has been submitted, process data
        return HttpResponseRedirect(request.get_full_path() )
    related = get_related(obj)
    for rel,objs in related.items():
        l = []
        for ob in objs:
            if 'get_linked' in dir(ob):
                l.append( ob.get_linked())
            else:
                l.append({'main': ob})

        related[rel]=l         

    return render(request, 'music/multidelete.html', {'related': related})

