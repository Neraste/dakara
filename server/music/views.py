from django.contrib import messages
from django.forms.models import modelformset_factory, modelform_factory, inlineformset_factory
from django import forms
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q

from music.models import *
from music.forms import *

from utils import get_related, get_name

from itertools import chain

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
        return HttpResponseRedirect(reverse(Model.__name__.lower() + '_merge', args=[id]))

    DeleteForm = modelform_factory(Model, fields=[] ) #form without any fields, used to check csrf token

    if request.method == 'POST': 
        del_form = DeleteForm(request.POST,instance=obj)

        if del_form.is_valid():#check csrf token
            obj.delete()
            messages.success(request, 'Object sucessfully deleted ^^')
            return HttpResponseRedirect(reverse(get_name(Model, plural = True) + '_edit') )
    else:
        del_form = DeleteForm(instance=obj)
    return render(request, 'music/multi/delete.html', {'obj': obj, 'form': del_form})

def multi_merge(request, id, Model):
    obj = get_object_or_404(Model,pk=id)
    related = get_related(obj)
    
    if not related: #If there are no related objects, we cannot merge it, redirect to delete page
        return HttpResponseRedirect(reverse(get_name(Model) + '_del', args=[id]))

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
            return HttpResponseRedirect(reverse(get_name(Model, plural = True) + '_edit'))
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

def artist_list(request):
    '''List artists'''
    artists = Artist.objects.all()
    artists_processed = artist_list_processor(artists)

    c = {
            'artists': artists_processed,
            'object_class': get_name(Artist),
            }

    return render(request, 'music/artist/list.html', c)
    

def artist_new(request):
    '''Create a new artist, with a person and multiple person names'''
    Form = modelform_factory(Artist, exclude = ('person',))
    FormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, extra = 1, can_delete = False)
    if request.method == 'POST':
        person = Person()
        form = Form(request.POST)
        form_set = FormSet(request.POST, instance = person)
        if form.is_valid() and form_set.is_valid():
            person.save()
            form_set.save()
            artist = form.save(commit = False)
            artist.person = person
            artist.save()
            messages.success(request, "New artist sucessfully created")

            return HttpResponseRedirect(reverse(get_name(Artist) + '_edit', args = [artist.id])) # redirection to brand new artist edit page

        else:
            messages.error(request, "Please check fields")

    else:
        form = Form()
        form_set = FormSet()

    c = {
            'name_form_set': form_set,
            'form': form,
            }

    return render(request, 'music/single/edit.html', c)

def artist_detail_delete(request, id):
    '''Show artist data and musics and can delete them'''
    artist = get_object_or_404(Artist, pk = id)
    musics = artist.music_set.all()

    delete = {} # form container
    delete['enabled'] = False if musics else True
    
    main_name = artist.person.main_name
    other_names = artist.person.personname_set.filter(is_main = False)
    
    DeleteForm = modelform_factory(Artist, fields=[]) #form without any fields, used to check csrf token
    if request.method == 'POST':
        delete_form = DeleteForm(request.POST, instance = artist)
        delete['form'] = delete_form
        if delete['enabled']:
            if delete_form.is_valid():
                artist.delete()
                messages.success(request, 'Artist sucessfully deleted')
                return HttpResponseRedirect(reverse(get_name(Artist, plural = True) + '_list'))

        else:
            messages.error(request, "Cannot delete an artist with dependent musics")
    
    else:
        delete_form = DeleteForm(instance = artist)
        delete['form'] = delete_form
                
    c = {
            'artist': artist,
            'main_name': main_name,
            'other_names': other_names,
            'musics': musics,
            'delete': delete,
            }
    
    return render(request, 'music/artist/detail.html', c)

def artist_edit(request, id):
    '''Edit artist then his person and multiple person names'''
    Form = modelform_factory(Artist, exclude = ('person',))
    FormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, extra = 1, can_delete = True)
    artist = get_object_or_404(Artist, pk = id)
    person = artist.person
    if request.method == 'POST':
        form = Form(request.POST, instance = artist)
        form_set = FormSet(request.POST, instance = person)

        if form.is_valid() and form_set.is_valid():
            form.save()
            form_set.save()
            messages.success(request, "Artist successfully edited")

            return HttpResponseRedirect(request.get_full_path())

        else:
            messages.error(request, "Please check fields")

    else:
        form = Form(instance = artist)
        form_set = FormSet(instance = person, queryset = PersonName.objects.order_by('-is_main', 'name', 'name_origin')) # this queryset sorts the forms (main name first, then names alphabeticaly); cannot be done in NameInlineFormSet class because specific to PersonName class

    c = {
            'name_form_set': form_set,
            'form': form,
            }

    return render(request, 'music/single/edit.html', c)

def artist_search(request):
    '''Search artists through names'''

    if request.method != 'GET' or not 'keywords' in request.GET or not request.GET['keywords']:
        return HttpResponseRedirect(reverse(get_name(Artist, plural = True) + '_list')) # redirection to artists list page

    keywords = request.GET['keywords']
    artists = Artist.objects.filter(
            Q(person__personname__name__icontains = keywords) |
            Q(person__personname__name_origin__icontains = keywords) |
            Q(person__personname__surname__icontains = keywords) |
            Q(person__personname__surname_origin__icontains = keywords)
            )
    artists = list(set(artists)) # same results merged
    amount = len(artists)
    artists_processed = artist_list_processor(artists)

    c = {
            'artists': artists_processed,
            'artists_amount': amount,
            'keywords': keywords,
            'object_class': get_name(Artist),
            }
    
    return render(request, 'music/artist/search.html', c)

def artist_list_processor(artists):
    '''Process artists to be displayed as a list with following pieces of information:
        - id,
        - main name,
        - music amount the artist has worked on,
        - list of roles the artist has worked as'''
    artists_processed = [{
        'id': artist.id,
        'main_name': artist.person.main_name,
        'music_amount': artist.music_set.count(),
        'roles': list(set(chain.from_iterable(
            [artistmusic.roles.all() for artistmusic in artist.artistmusic_set.all()]
            ))),
        } for artist in artists]

    return artists_processed

def opus_list(request):
    '''List opusess'''
    opuses = Opus.objects.all()
    opuses_processed = opus_list_processor(opuses)

    c = {
            'opuses': opuses_processed,
            'object_class': get_name(Opus),
            }

    return render(request, 'music/opus/list.html', c)

def opus_new(request):
    '''Create a new opus, with an item and multiple item names'''
    Form = modelform_factory(Opus, exclude = ('item',))
    FormSet = inlineformset_factory(Item, ItemName, formset = NameInlineFormSet, extra = 1, can_delete = False)
    if request.method == 'POST':
        item = Item()
        form = Form(request.POST)
        form_set = FormSet(request.POST, instance = item)
        if form.is_valid() and form_set.is_valid():
            item.save()
            form_set.save()
            opus = form.save(commit = False)
            opus.item = item
            opus.save()
            messages.success(request, "New opus successfully created")

            return HttpResponseRedirect(reverse(get_name(Opus) + '_edit', args = [opus.id])) # redirection to brand new opus edit page

        else:
            messages.error(request, "Please check fields")

    else:
        form = Form()
        form_set = FormSet()

    c = {
            'name_form_set': form_set,
            'form': form,
            }

    return render(request, 'music/single/edit.html', c)
    

def opus_detail_delete(request, id):
    '''Show opus data and musics and can delete them'''
    opus = get_object_or_404(Opus, pk = id)
    musics = opus.music_set.all()

    delete = {} # form container
    delete['enabled'] = False if musics else True
    
    main_name = opus.item.main_name
    other_names = opus.item.itemname_set.filter(is_main = False)
    
    DeleteForm = modelform_factory(Opus, fields=[]) #form without any fields, used to check csrf token
    if request.method == 'POST':
        delete_form = DeleteForm(request.POST, instance = opus)
        delete['form'] = delete_form
        if delete['enabled']:
            if delete_form.is_valid():
                opus.delete()
                messages.success(request, 'Opus sucessfully deleted')
                return HttpResponseRedirect(reverse(get_name(Opus, plural = True) + '_list'))

        else:
            messages.error(request, "Cannot delete an opus with dependent musics")
    
    else:
        delete_form = DeleteForm(instance = opus)
        delete['form'] = delete_form
                
    c = {
            'opus': opus,
            'main_name': main_name,
            'other_names': other_names,
            'musics': musics,
            'delete': delete,
            }
    
    return render(request, 'music/opus/detail.html', c)

def opus_edit(request, id):
    '''Edit opus then its item and multiple item names'''
    Form = modelform_factory(Opus, exclude = ('item',))
    FormSet = inlineformset_factory(Item, ItemName, formset = NameInlineFormSet, extra = 1, can_delete = True)
    opus = get_object_or_404(Opus, pk = id)
    item = opus.item
    if request.method == 'POST':
        form = Form(request.POST, instance = opus)
        form_set = FormSet(request.POST, instance = item)

        if form.is_valid() and form_set.is_valid():
            form.save()
            form_set.save()
            messages.success(request, "Opus successfully edited")

            return HttpResponseRedirect(request.get_full_path())

        else:
            messages.error(request, "Please check fields")

    else:
        form = Form(instance = opus)
        form_set = FormSet(instance = item, queryset = ItemName.objects.order_by('-is_main', 'name', 'name_origin')) # this queryset sorts the forms (main name first, then names alphabeticaly); cannot be done in NameInlineFormSet class because specific to ItemName class

    c = {
            'name_form_set': form_set,
            'form': form,
            }

    return render(request, 'music/single/edit.html', c)

def opus_search(request):
    '''Search opuses through names'''
    
    if request.method != 'GET' or not 'keywords' in request.GET or not request.GET['keywords']:
        return HttpResponseRedirect(reverse(get_name(Opus, plural = True) + '_list')) # redirection to opuses list page

    keywords = request.GET['keywords']
    opuses = Opus.objects.filter(
            Q(item__itemname__name__icontains = keywords) |
            Q(item__itemname__name_origin__icontains = keywords)
            )
    opuses = list(set(opuses)) # same results merged
    amount = len(opuses)
    opuses_processed = opus_list_processor(opuses)

    c = {
            'opuses': opuses_processed,
            'opuses_amount': amount,
            'keywords': keywords,
            'object_class': get_name(Opus),
            }
    
    return render(request, 'music/opus/search.html', c)
    pass

def opus_list_processor(opuses):
    '''Process opuses to be displayed as a list with following pieces of information:
        - id,
        - main name,
        - music amount for this opus,
        - date'''
    artists_processed = [{
        'id': opus.id,
        'main_name': opus.item.main_name,
        'music_amount': opus.music_set.count(),
        'date': opus.date,
        } for opus in opuses]

    return artists_processed
