from django.contrib import messages
from django.forms.models import modelformset_factory, modelform_factory, inlineformset_factory
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
    return render(request, 'music/multi/edit.html', {'formSet': f_set})


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
    return render(request, 'music/multi/delete.html', {'obj': obj, 'form': del_form})

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

    return render(request, 'music/multi/merge.html', {'obj': obj, 'related': related_list,'form': merge_form})

def people_list(request, Model):
    '''List artists or timers'''
    objects = Model.objects.all()

    c = {
            'objects': objects,
            }

    return render(request, 'music/people/list.html', c)

def people_new(request, Model):
    '''Create a new artist or timer, with a person and multiple person names'''
    PageFormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, exclude = ('is_main',), extra = 1, can_delete = False)
    SaveFormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, extra = 1, can_delete = False) # use of a dummy save form set, same as above but with is_main field enabled
    if request.method == 'POST':
        person = Person()
        page_form_set = PageFormSet(request.POST, instance = person)
        main = int(request.POST.get('main'))
        post_copy = request.POST.copy()
        for index, form in enumerate(page_form_set):
            post_copy[form.prefix + '-is_main'] = True if main == index else False # alteration of POST data for dummy save form set
        
        save_form_set = SaveFormSet(post_copy, instance = person)
        main_name_form = MainNameForm(request.POST) # use of a special form for main name determination
        main_name_form.initial['main'] = main
            
        if save_form_set.is_valid(): # check on dummy
            person.save()
            save_form_set.save()
            guy = Model(person = person) # a guy is either an Artist, or a Timer
            guy.save()
            messages.success(request, "New person created successfully")

            return HttpResponseRedirect(reverse(Model.__name__.lower() + 's_edit', args = [guy.id])) # redirection to brand new guy edit page

        else:
            messages.error(request, "Please check fields")

    else:
        page_form_set = PageFormSet()
        main_name_form = MainNameForm(target = page_form_set)

    c = {
            'name_form_set': page_form_set,
            'main_form': main_name_form,
            }

    return render(request, 'music/people/edit.html', c)

def people_detail(request, Model, id):
    '''Used by artist_detail and timer_detail to show artist or timer data and musics'''
    guy = get_object_or_404(Model, pk = id) # a guy is either an Artist, or a Timer
    if Model == Artist:
        musics = guy.music_set.all()
    elif Model == Timer:
        musics = [subtitle.music for subtitle in guy.subtitle_set.all()] #TODO further treatment?
    else:
        musics = [] #TODO add error if unconsistent Model

    main_name = guy.person.main_name
    other_names = guy.person.personname_set.filter(is_main = False)

    c = {
            'guy': guy,
            'main_name': main_name,
            'other_names': other_names,
            'musics': musics,
            }
    
    return render(request, 'music/people/detail.html', c)

def people_edit(request, Model, id):
    '''Edit artist or timer, then his person and multiple person names'''
    PageFormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, exclude = ('is_main',), extra = 1, can_delete = True)
    SaveFormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, extra = 1, can_delete = True) # use of a dummy save form set, same as above but with is_main field enabled
    guy = get_object_or_404(Model, pk = id) # a guy is either an Artist, or a Timer
    person = guy.person
    if request.method == 'POST':
        page_form_set = PageFormSet(request.POST, instance = person)
        main = int(request.POST.get('main'))
        post_copy = request.POST.copy()
        for index, form in enumerate(page_form_set):
            post_copy[form.prefix + '-is_main'] = True if main == index else False # alteration of POST data for dummy save form set
        
        save_form_set = SaveFormSet(post_copy, instance = person)
        main_name_form = MainNameForm(request.POST) # use of a special form for main name determination
        main_name_form.initial['main'] = main

        if save_form_set.is_valid(): # check on dummy
            save_form_set.save()
            messages.success(request, "Person successfully edited")

            return HttpResponseRedirect(request.get_full_path())

        else:
            messages.error(request, "Please check fields")

    else:
        page_form_set = PageFormSet(instance = person, queryset = PersonName.objects.order_by('-is_main', 'name', 'name_transliterated')) # this queryset sorts the forms (main name first, then names alphabeticaly); cannot be done in NameInlineFormSet class because specific to PersonName class
        main_name_form = MainNameForm(target = page_form_set)

    c = {
            'name_form_set': page_form_set,
            'main_form': main_name_form,
            }

    return render(request, 'music/people/edit.html', c)
    
def people_delete(request, Model, id):
    pass #TODO
