from django.contrib import messages
from django.forms.models import modelformset_factory, modelform_factory
from django import forms
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
    obj = get_object_or_404(Model,pk=id)
    related = get_related(obj)
    

    if related: #If there are related objects, we cannot delete it, redirect to merge page
        return HttpResponseRedirect(request.get_full_path() + "merge/")

    DeleteForm = modelform_factory(Model, fields=[] ) #form without any fields, used to check csrf token

    if request.method == 'POST': 
        del_form = DeleteForm(request.POST,instance=obj)

        if del_form.is_valid():#check csrf token
            obj.delete()
            messages.success(request, 'Object sucessfully deleted ^^')
            return HttpResponseRedirect(dirname(dirname(request.get_full_path())) )
    else:
        del_form = DeleteForm(instance=obj)
    return render(request, 'music/multidelete.html', {'obj': obj, 'form': del_form})

def multi_merge(request, id, Model):
    obj = get_object_or_404(Model,pk=id)
    related = get_related(obj)
    
    if not related: #If there are no related objects, we cannot merge it, redirect to delete page
        return HttpResponseRedirect(dirname(dirname(request.get_full_path())) )

    merge_queryset = Model.objects.exclude(pk=id) # Queryset with opions to merge to
    class MergeForm(forms.Form):
        merge_to = forms.ModelChoiceField(queryset = merge_queryset)


    if request.method == 'POST': 
        merge_form = MergeForm(request.POST)

        if merge_form.is_valid():
            #for every related object change the relation to the supplied object
            merge_to =  merge_form.cleaned_data['merge_to']
            for rel,objs in related.items():
                field = rel.field
                print field
                for ob in objs:
                    if type(field) is models.fields.related.ForeignKey : #in case of of one to many field, replace it
                        setattr(ob,field.name,merge_to)
                        ob.save()
                    if type(field) is models.fields.related.ManyToManyField : #for many to many, remove the old one and add the new
                        getattr(ob,field.name).add(merge_to)
                        getattr(ob,field.name).remove(obj)
                        ob.save()
            messages.success(request, 'Merge sucessful  ^^')
            return HttpResponseRedirect(dirname(dirname(request.get_full_path())) )
        else:
            messages.error(request,'Invalid form')
    else:
        merge_form = MergeForm()

    #pre process related objects to display in template
    related_list = {} 
    for rel,objs in related.items():
        l = []
        for ob in objs:
            if 'get_linked' in dir(ob):
                l.append( ob.get_linked())
            else:
                l.append({'main': ob})
        related_list[rel.model.__name__]=l         

    return render(request, 'music/multimerge.html', {'obj': obj, 'related': related_list,'form': merge_form})

