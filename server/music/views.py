from django.contrib import messages
from django.forms.models import modelformset_factory, modelform_factory
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from music.models import *
from music.forms import *

from utils import get_related

from os.path import dirname

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
    DeleteForm = modelform_factory(Model, fields=[] ) #form without any fields, use to check csrf token

    obj = get_object_or_404(Model,pk=id)

    if request.method == 'POST': 
        form = DeleteForm(request.POST,instance=obj)
        if form.is_valid():#check csrf token
            obj.delete()
            messages.success(request, 'Object sucessfully deleted ^^')
            return HttpResponseRedirect(dirname(dirname(request.get_full_path())) )

    related = get_related(obj)

    has_related = False
    for rel,objs in related.items():
        l = []
        for ob in objs:
            has_related = True
            if 'get_linked' in dir(ob):
                l.append( ob.get_linked())
            else:
                l.append({'main': ob})
        related[rel]=l         

    form = DeleteForm(instance=obj)
    return render(request, 'music/multidelete.html', {'related': related,'has_r': has_related,'form': form})

