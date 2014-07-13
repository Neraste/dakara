from django.contrib import messages
from django.forms.models import modelformset_factory, modelform_factory, inlineformset_factory

from django import forms
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import DatabaseError
from django.utils.text import slugify

from music.models import *
from name.models import *
from music.forms import *
from name.forms import *

from utils import *

from itertools import chain
from re import match

# Multi area ##################################################################

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

# Artist area #################################################################

def artist_list(request):
    '''List artists'''
    artists = Artist.objects.all()#.order_by('person__personname__name', 'person__personname__surname', 'person__personname__name_origin', 'person__personname__surname_origin').distinct()
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

            return HttpResponseRedirect(reverse(get_name(Artist) + '_detail_delete', args = [artist.id])) # redirection to brand new artist page

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
    musics = artist.music_set.all().order_by('item__itemname__name', 'item__itemname__name_origin', 'version')
    musics_processed = music_list_processor(musics)
    hide = {
            'artist': True,
    }

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
            'musics': musics_processed,
            'delete': delete,
            'hide': hide,
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

            return HttpResponseRedirect(reverse(get_name(Artist) + '_detail_delete', args = [artist.id])) # redirection to artist page

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
    (artists, amount) = artist_search_processor(keywords)
    artists_processed = artist_list_processor(artists)

    c = {
            'artists': artists_processed,
            'artists_amount': amount,
            'keywords': keywords,
            'object_class': get_name(Artist),
            }
    
    return render(request, 'music/artist/search.html', c)

def artist_search_processor(keywords):
    '''Process artist search and gives:
        - List of unique artists
        - Amount of artists'''
    artists = Artist.objects.filter(
            Q(person__personname__name__icontains = keywords) |
            Q(person__personname__name_origin__icontains = keywords) |
            Q(person__personname__surname__icontains = keywords) |
            Q(person__personname__surname_origin__icontains = keywords)
            ).distinct()
    
    amount = len(artists)

    return (artists, amount)

def artist_list_processor(artists):
    '''Process artists to be displayed as a sorten list with following pieces of information:
        - id,
        - main name,
        - music amount the artist has worked on,
        - list of roles the artist has worked as'''
    artists_list = person_sort(artists)
    artists_processed = [{
        'id': artist.id,
        'main_name': artist.person.main_name,
        'music_amount': artist.music_set.count(),
        'roles': list(set(chain.from_iterable(
            [artistmusic.roles.all() for artistmusic in artist.artistmusic_set.all()]
            ))),
        } for artist in artists_list]

    return artists_processed

# Opus area ###################################################################

def opus_list(request, opus_type = None):
    '''List opuses, filtered by opus type if any'''
    if opus_type:
        opus_type_string = opus_type.lower() # clean opus_type
        opus_type_obj_list = OpusType.objects.all()
        opus_type_string_list = [ot.name_slug for ot in opus_type_obj_list]
        if opus_type_string in opus_type_string_list: # look for opus type in opus type (slugified) list
            opus_type_obj = OpusType.objects.get(name_slug__iexact = opus_type_string)
            opuses = Opus.objects.filter(opus_type = opus_type_obj)

        else: # if opus type not in list, ask for a global opus list
            return HttpResponseRedirect(reverse(get_name(Opus, plural = True) + '_list'))

    else:
        opuses = Opus.objects.all()
        opus_type_obj = None

    opuses_processed = opus_list_processor(opuses)

    c = {
            'opus_type': opus_type_obj,
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

            return HttpResponseRedirect(reverse(get_name(Opus) + '_detail_delete', args = [opus.id])) # redirection to brand new opus page

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
    musics = opus.music_set.all().order_by('item__itemname__name', 'item__itemname__name_origin', 'version')
    musics_processed = music_list_processor(musics)
    hide = {
            'opus': True,
            }

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
            'musics': musics_processed,
            'delete': delete,
            'hide': hide,
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

            return HttpResponseRedirect(reverse(get_name(Opus) + '_detail_delete', args = [opus.id])) # redirection to opus page

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
    (opuses, amount) = opus_search_processor(keywords)
    opuses_processed = opus_list_processor(opuses)

    c = {
            'opuses': opuses_processed,
            'opuses_amount': amount,
            'keywords': keywords,
            'object_class': get_name(Opus),
            }
    
    return render(request, 'music/opus/search.html', c)

def opus_search_processor(keywords):
    '''Process opus search and gives:
        - List of unique opuses
        - Amount of opuses'''
    opuses = Opus.objects.filter(
            Q(item__itemname__name__icontains = keywords) |
            Q(item__itemname__name_origin__icontains = keywords)
            ).distinct()
    
    amount = len(opuses)

    return (opuses, amount)

def opus_list_processor(opuses):
    '''Process opuses to be displayed as a list with following pieces of information:
        - id,
        - main name,
        - music amount for this opus,
        - date'''
    opuses_list = item_sort(opuses)
    opuses_processed = [{
        'id': opus.id,
        'main_name': opus.item.main_name,
        'music_amount': opus.music_set.count(),
        'date': opus.date,
        } for opus in opuses_list]

    return opuses_processed

# Music area ##################################################################

def music_list(request):
    '''List musics'''
    musics = Music.objects.all()
    musics_processed = music_list_processor(musics)

    c = {
            'musics': musics_processed,
            'object_class': get_name(Music),
            }

    return render(request, 'music/music/list.html', c)

def music_new(request):
    '''Create a new music, with an item and multiple item names and all relevant data'''
    MusicForm = modelform_factory(Music, exclude = ('item', 'artists', 'uses'))
    NameFormSet = inlineformset_factory(Item, ItemName, formset = NameInlineFormSet, extra = 1, can_delete = False)
    ArtistFormSet = inlineformset_factory(Music, ArtistMusic, extra = 1, can_delete = False)
    UseFormSet = inlineformset_factory(Music, MusicOpus, extra = 1, can_delete = False)
    AudioFormSet = inlineformset_factory(Music, Audio, formset = StreamInlineFormSet, extra = 1, can_delete = False)
    VideoFormSet = inlineformset_factory(Music, Video, formset = StreamInlineFormSet, extra = 1, can_delete = False)
    SubtitleFormSet = inlineformset_factory(Music, Subtitle, extra = 1, can_delete = False)
    if request.method == 'POST':
        music_form = MusicForm(request.POST)
        item = Item()
        name_form_set = NameFormSet(request.POST, instance = item)
        artist_form_set = ArtistFormSet(request.POST)
        use_form_set = UseFormSet(request.POST)
        audio_form_set = AudioFormSet(request.POST)
        video_form_set = VideoFormSet(request.POST)
        subtitle_form_set = SubtitleFormSet(request.POST)

        if music_form.is_valid() and name_form_set.is_valid(): 
            music = music_form.save(commit = False) # save music without commiting it only to get and id
            artist_form_set = ArtistFormSet(request.POST, instance = music)
            use_form_set = UseFormSet(request.POST, instance = music)
            audio_form_set = AudioFormSet(request.POST, instance = music)
            video_form_set = VideoFormSet(request.POST, instance = music)
            subtitle_form_set = SubtitleFormSet(request.POST, instance = music)
            if artist_form_set.is_valid() and use_form_set.is_valid() and audio_form_set.is_valid() and video_form_set.is_valid() and subtitle_form_set.is_valid():
                item.save()
                music.item = item
                music.save()
                name_form_set.save()
                artist_form_set.save()
                use_form_set.save()
                audio_form_set.save()
                video_form_set.save()
                subtitle_form_set.save()
                messages.success(request, "New music successfully created")

                return HttpResponseRedirect(reverse(get_name(Music) + '_detail_delete', args = [music.id])) # redirection to brand new music page

            else:
                messages.error(request, "Please check fields")
            
        else:
            messages.error(request, "Please check fields")

    else:
        music_form = MusicForm()
        name_form_set = NameFormSet()
        artist_form_set = ArtistFormSet()
        use_form_set = UseFormSet()
        audio_form_set = AudioFormSet()
        video_form_set = VideoFormSet()
        subtitle_form_set = SubtitleFormSet()

    c = {
            'name_form_set': name_form_set,
            'artist_form_set': artist_form_set,
            'use_form_set': use_form_set,
            'audio_form_set': audio_form_set,
            'video_form_set': video_form_set,
            'subtitle_form_set': subtitle_form_set,
            'form': music_form,
            }

    return render(request, 'music/music/edit.html', c)

def music_detail_delete(request, id):
    '''Show music data and can delete it'''
    music = get_object_or_404(Music, pk = id)

    delete = {} # form container
    delete['enabled'] = True
    
    main_name = music.item.main_name
    other_names = music.item.other_names
    
    DeleteForm = modelform_factory(Opus, fields=[]) #form without any fields, used to check csrf token
    if request.method == 'POST':
        delete_form = DeleteForm(request.POST, instance = music)
        delete['form'] = delete_form
        if delete_form.is_valid():
            music.delete()
            messages.success(request, 'Music sucessfully deleted')
            return HttpResponseRedirect(reverse(get_name(Music, plural = True) + '_list'))

    else:
        delete_form = DeleteForm(instance = music)
        delete['form'] = delete_form
                
    c = {
            'music': music,
            'main_name': main_name,
            'other_names': other_names,
            'delete': delete,
            }
    
    return render(request, 'music/music/detail.html', c)

def music_edit(request, id):
    '''Edit music then its item and multiple item names and all relevant data'''
    MusicForm = modelform_factory(Music, exclude = ('item', 'artists', 'uses'))
    NameFormSet = inlineformset_factory(Item, ItemName, formset = NameInlineFormSet, extra = 1, can_delete = True)
    ArtistFormSet = inlineformset_factory(Music, ArtistMusic, extra = 1, can_delete = True)
    UseFormSet = inlineformset_factory(Music, MusicOpus, extra = 1, can_delete = True)
    AudioFormSet = inlineformset_factory(Music, Audio, formset = StreamInlineFormSet, extra = 1, can_delete = True)
    VideoFormSet = inlineformset_factory(Music, Video, formset = StreamInlineFormSet, extra = 1, can_delete = True)
    SubtitleFormSet = inlineformset_factory(Music, Subtitle, extra = 1, can_delete = True)
    music = get_object_or_404(Music, pk = id)
    item = music.item
    if request.method == 'POST':
        music_form = MusicForm(request.POST, instance = music)
        name_form_set = NameFormSet(request.POST, instance = item)
        artist_form_set = ArtistFormSet(request.POST, instance = music)
        use_form_set = UseFormSet(request.POST, instance = music)
        audio_form_set = AudioFormSet(request.POST, instance = music)
        video_form_set = VideoFormSet(request.POST, instance = music)
        subtitle_form_set = SubtitleFormSet(request.POST, instance = music)

        if music_form.is_valid() and name_form_set.is_valid() and artist_form_set.is_valid() and use_form_set.is_valid() and audio_form_set.is_valid() and video_form_set.is_valid() and subtitle_form_set.is_valid():
            music_form.save()
            name_form_set.save()
            artist_form_set.save()
            music.item = item
            use_form_set.save()
            audio_form_set.save()
            video_form_set.save()
            subtitle_form_set.save()
            messages.success(request, "Music successfully edited")

            return HttpResponseRedirect(reverse(get_name(Music) + '_detail_delete', args = [music.id])) # redirection to music page

        else:
            messages.error(request, "Please check fields")

    else:
        music_form = MusicForm(instance = music)
        name_form_set = NameFormSet(instance = item, queryset = ItemName.objects.order_by('-is_main', 'name', 'name_origin')) # this queryset sorts the forms (main name first, then names alphabeticaly); cannot be done in NameInlineFormSet class because specific to ItemName class
        artist_form_set = ArtistFormSet(instance = music)
        use_form_set = UseFormSet(instance = music)
        audio_form_set = AudioFormSet(instance = music)
        video_form_set = VideoFormSet(instance = music)
        subtitle_form_set = SubtitleFormSet(instance = music)

    c = {
            'name_form_set': name_form_set,
            'artist_form_set': artist_form_set,
            'use_form_set': use_form_set,
            'audio_form_set': audio_form_set,
            'video_form_set': video_form_set,
            'subtitle_form_set': subtitle_form_set,
            'form': music_form,
            }

    return render(request, 'music/music/edit.html', c)

def music_search(request):
    '''Search musics through names'''

    if request.method != 'GET' or not 'keywords' in request.GET or not request.GET['keywords']:
        return HttpResponseRedirect(reverse(get_name(Music, plural = True) + '_list')) # redirection to musics list page

    keywords = request.GET['keywords']
    (musics, amount) = music_search_processor(keywords)
    musics_processed = music_list_processor(musics)

    c = {
            'musics': musics_processed,
            'musics_amount': amount,
            'keywords': keywords,
            'object_class': get_name(Music),
            }
    
    return render(request, 'music/music/search.html', c)

def music_search_processor(keywords):
    '''Process music search and gives:
        - List of unique musics
        - Amount of musics'''
    musics = Music.objects.filter(
            Q(item__itemname__name__icontains = keywords) |
            Q(item__itemname__name_origin__icontains = keywords) |
            Q(version = keywords)
            ).distinct()
    amount = len(musics)
    return (musics, amount)

def music_list_processor(musics):
    '''Process musicss to be displayed as a list with following pieces of information:
        - id,
        - main name,
        - version,
        - (main) artist,
        - first exact use,
        - duration,
        - has instrumental,
        - is short,
        - is remix,
        - is cover,'''
    musics_list = item_sort(musics)
    musics_processed = [{
        'id': music.id,
        'main_name': music.item.main_name,
        'version': music.version,
        'artist': music.main_artist,
        'use': music.main_exact_use,
        'duration': music.duration,
        'has_instrumental': music.has_instrumental,
        'is_short': music.is_short,
        'is_remix': music.is_remix,
        'is_cover': music.is_cover,
        } for music in musics_list]

    return musics_processed

# Global search area ##########################################################

def global_search(request):
    '''Search for music, artist or opus with one fielded keywords in different steps:
    1. Unsplitted keywords are contained in:
        - Music:
            + names,
            + version,
        - Artist:
            + names,
        - Opus:
            + names,
    2. Splitted keywords are regrouped and have to all be contained in any of:
        - Music:
            + names,
            + version,
            + uses opus names,
            + short/long use types concatenated with use versions,
            + artists names,
            + videos opus names'''
    if request.method != 'GET' or not 'keywords' in request.GET or not request.GET['keywords']:
        c = {
                'no_entry': True,
                }

        return render(request, 'music/global/search.html', c)

    keywords = request.GET['keywords']

    # Keyword preprocess
    reg = match(r'^((.*)(\w))+(\s)?$', keywords) # let's separate final spaces
    if reg and reg.lastindex > 1: #should be always true
        keywords = reg.group(1)

    # Step 1
    (musics, music_amount) = music_search_processor(keywords)
    (artists, artist_amount) = artist_search_processor(keywords)
    (opuses, opus_amount) = opus_search_processor(keywords)

    if musics or artists or opuses: # if at least one music, artist or opus have been found
        musics_processed =  music_list_processor(musics)
        artists_processed = artist_list_processor(artists)
        opuses_processed = opus_list_processor(opuses)
        total_amount = music_amount + artist_amount + opus_amount

        c = {
                'musics': musics_processed,
                'music_amount': music_amount,
                'artists': artists_processed,
                'artist_amount': artist_amount,
                'opuses': opuses_processed,
                'opus_amount': opus_amount,
                'total_amount': total_amount,
                'global_keywords': keywords,
                }

        return render(request, 'music/global/search.html', c)

    # Step 2
    def query_factory(kw):
        '''Make the main query'''
        query = Q(
                # Names
                Q(item__itemname__name__icontains = kw) |
                Q(item__itemname__name_origin__icontains = kw) |
                # Version
                Q(version = kw) |
                # Use names
                Q(musicopus__opus__item__itemname__name__icontains = kw) |
                Q(musicopus__opus__item__itemname__name_origin__icontains = kw) |
                # Use type
                Q(musicopus__use_type__name_long__icontains = kw) |
                Q(musicopus__use_type__name_short__icontains = kw) |
                # Artist names
                Q(artistmusic__artist__person__personname__name__icontains = kw) |
                Q(artistmusic__artist__person__personname__name_origin__icontains = kw) |
                Q(artistmusic__artist__person__personname__surname__icontains = kw) |
                Q(artistmusic__artist__person__personname__surname_origin__icontains = kw) |
                # Video opus names
                Q(video__opus__item__itemname__name__icontains = kw) |
                Q(video__opus__item__itemname__name_origin__icontains = kw)
                )
        
        return query

    def query_use_type_version_factory(kw_alph, kw_num = None):
        '''Make a query for alphabetic short or long  use type and numeric version'''
        query = Q(
                    Q(musicopus__use_type__name_short__icontains = kw_alph) |
                    Q(musicopus__use_type__name_long__icontains = kw_alph)
                    )
        if kw_num:
            query &= Q(musicopus__version__exact = kw_num)

        return query

    def query_use_type_unspaced_factory(kw, second_chance = False):
        '''Short (and long) name use type and version detection in a single kw (eg "OP1")
        Uses only name use type if second chance requested'''
        reg = match(r'^(\D+)(\d+)$', kw)
        query = Q()
        out_dict = {
                'try': False,
                }
        if reg:
            kw_alph = reg.group(1)
            kw_num = reg.group(2)
            if second_chance:
                query = query_use_type_version_factory(kw_alph)
            else:
                query = query_use_type_version_factory(kw_alph, kw_num)

            out_dict = {
                    'try': True,
                    'retry': second_chance,
                    'alph': kw_alph,
                    'num': kw_num,
                    }

        return (query, out_dict)

    def query_use_type_spaced_factory(gkw):
        '''Long (and short) name use type and version detection in a gkw of at least 2 kw (eg "Opening 1")'''
        kw_list = gkw.split()
        query = Q()
        if kw_list[-1].isdigit() and len(kw_list) > 1:
            kw_alph = u''.join(kw_list[0:-1])
            kw_num = kw_list[-1]
            query = query_use_type_version_factory(kw_alph, kw_num)

        return query

    keywords_splitted = keywords.split()
    keywords_amount = len(keywords_splitted)

    results = [] # debug purpose
    unmatched_kw = [] # debug purpose

    i = 0
    latest_gkw_musics = None
    g_first_kw = True # first kw of a group
    first_g = True # first group
    use_type_unspaced_retry_request = False
    try:
        while True: # loop for amount of kw plus some extra re-loops
            # kw loading
            kw = keywords_splitted[i]
            
            # query
            if first_g: # first group
                musics = Music.objects

            if g_first_kw: # first kw of the group
                gkw = kw
                (query_use_type, use_type_unspaced) = query_use_type_unspaced_factory(gkw, use_type_unspaced_retry_request)

            else: # any other kw of any other group
                gkw += ' ' + kw
                query_use_type = query_use_type_spaced_factory(gkw)
            
            query = query_factory(gkw)
            gkw_musics = musics.filter(query | query_use_type) # each gkw query filters previous group result

            # check matching
            if gkw_musics: # if musics remain, let's save and continue
                if use_type_unspaced['try'] and use_type_unspaced['retry']:
                    use_type_unspaced_retry_request = False
                    gkw = use_type_unspaced['alph']
                    unmatched_kw.append(use_type_unspaced['num'])

                latest_gkw_musics = gkw_musics
                new_result = {
                        'gkw': gkw,
                        'musics': gkw_musics,
                        }
                
                if first_g:
                    first_g = False

                if g_first_kw: # if first group kw, let's down the flag and new save
                    results.append(new_result)
                    g_first_kw = False

                else: # else, nothing but update save
                    results[-1] = new_result

                # if matching sucessfull, let's continue with another kw
                if keywords_amount - 1 == i: # if last kw processed, end of operation
                    break

                else: # else continue
                    i += 1
                
            else: # if no music remains
                if use_type_unspaced['try']: # if a unspaced use type and version has been performed 
                    if not use_type_unspaced['retry']:
                        use_type_unspaced_retry_request = True
                        continue

                    else:
                        use_type_unspaced_retry = False

                if first_g: # first kw havn't a solely result, abort process
                    unmatched_kw.append(kw)
                    break

                else: # restore previous sucessful set of results, new group created
                    musics = latest_gkw_musics

                if g_first_kw: # if no music detected for this single kw, assume kw is invalid and continue
                    unmatched_kw.append(kw)
                    if keywords_amount - 1 == i: # if last kw processed, end of operation
                        break

                    else: # else continue
                        i += 1

                else: # previous group sucessfull, let's start a new group and analyse this kw again (no i incrementation)
                    g_first_kw = True
        
    except DatabaseError:
        c = {
                'database_error': True,
                'global_keywords': keywords,
                }
        
        return render(request, 'music/global/search.html', c)
    
    musics = latest_gkw_musics
    if musics: # if at least one music has been found
        musics = musics.distinct()
        music_amount = len(musics)
        musics_processed = music_list_processor(musics)

        groups = [result['gkw'] for result in results]

        c = {
                'musics': musics_processed,
                'music_amount': music_amount,
                'groups': groups,
                'unmatched': unmatched_kw,
                'global_keywords': keywords,
                }

        return render(request, 'music/global/search.html', c)

    # else, if nothing has been found
    c = {
            'nothing': True,
            'global_keywords': keywords,
            }

    return render(request, 'music/global/search.html', c)

def advanced_search(request):
    '''Search for music with several fields:
    - name,
    - version,
    - is short,
    - is remix,
    - is cover,
    - date,
    - languages,
    - duration: min and max,
    - (creation date)
    - (update date)
    - artists:
        + name,
    - use:
        + opus,
        + use type,
        + version,
        + (interval),
        + language,
    - audio:
        + has instrumental,
    - video:
        + realisator,
        + video type,
        + opus,
    - subtitle:
        + lyrics
        + timer.'''
    
    if request.method != 'GET':
        c = {
                'no_entry': True,
                'global_keywords': keywords,
                }

        return render(request, 'music/global/search.html', c)

    if request.GET: # if search requested, fill the form and process
        music_search_form = MusicSearchForm(request.GET)
        query = Q()
        get = request.GET
        if 'name' in get and get['name']:
            name = get['name']
            query &= Q(
                    Q(item__itemname__name__icontains = name) |
                    Q(item__itemname__name_origin__icontains = name)
                    )

        if 'version' in get and get['version']:
            version = get['version']
            query &= Q(version__icontains = version)

        if 'is_short' in get and get['is_short']:
            is_short = get['is_short']
            query &= Q(is_short = is_short)

        if 'is_remix' in get and get['is_remix']:
            is_remix = get['is_remix']
            query &= Q(is_remix = is_remix)

        if 'is_cover' in get and get['is_cover']:
            is_cover = get['is_cover']
            query &= Q(is_cover = is_cover)

        if 'date' in get and get['date']:
            date = get['date']
            query &= Q(date = date)

        if 'languages' in get and get['languages']:
            languages = get['languages']
            query &= Q(languages = languages)
        
        if 'duration_min' in get and get['duration_min']:
            duration_min = get['duration_min']
            query &= Q(duration__gte = duration_min)

        if 'duration_max' in get and get['duration_max']:
            duration_max = get['duration_max']
            query &= Q(duration__lte = duration_max)

        musics = Music.objects.filter(query)
        
        if musics:
            musics = musics.distinct()
            music_amount = len(musics)
            musics_processed = music_list_processor(musics)
        
            c = {
                    'form': music_search_form,
                    'musics': musics_processed,
                    'music_amount': music_amount,
                    }

            return render(request, 'music/global/advanced_search.html', c)
        
        else:
            c = {
                    'nothing': True,
                    'form': music_search_form,
                    }

            return render(request, 'music/global/advanced_search.html', c)

    else: # if search page just called, give empty form
        music_search_form = MusicSearchForm()

        c = {
                'form': music_search_form,
                }

        return render(request, 'music/global/advanced_search.html', c)
