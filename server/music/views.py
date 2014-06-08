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
    artists = Artist.objects.all().order_by('person__personname__name', 'person__personname__surname', 'person__personname__name_origin', 'person__personname__surname_origin')
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
            'hide': hidey,
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
            ).order_by('person__personname__name', 'person__personname__surname', 'person__personname__name_origin', 'person__personname__surname_origin')

    artists = list(set(artists)) # same results merged
    amount = len(artists)
    return (artists, amount)

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

# Opus area ###################################################################

def opus_list(request):
    '''List opusess'''
    opuses = Opus.objects.all().order_by('item__itemname__name', 'item__itemname__name_origin')
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
            ).order_by('item__itemname__name', 'item__itemname__name_origin')
    opuses = list(set(opuses)) # same results merged
    amount = len(opuses)

    return (opuses, amount)

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

# Music area ##################################################################

def music_list(request):
    '''List musics'''
    musics = Music.objects.all().order_by('item__itemname__name', 'item__itemname__name_origin', 'version')
    musics_processed = music_list_processor(musics)

    c = {
            'musics': musics_processed,
            'object_class': get_name(Music),
            }

    return render(request, 'music/music/list.html', c)

def music_new(request):
    pass

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
    pass

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
            ).order_by('item__itemname__name', 'item__itemname__name_origin', 'version')
    musics = list(set(musics)) # same results merged
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
        } for music in musics]

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
        pass #TODO

    keywords = request.GET['keywords']

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

    def query_use_type_version_factory(kw_alph, kw_num):
        '''Make a query for alphabetic short or long  use type and numeric version'''
        query = Q(
                (
                    Q(musicopus__use_type__name_short__icontains = kw_alph) |
                    Q(musicopus__use_type__name_long__icontains = kw_alph)
                    ) &
                Q(musicopus__version__exact = kw_num)
                )

        return query

    def query_use_type_unspaced_factory(kw):
        '''Short (and long) name use type and version detection in a single kw (eg "OP1")'''
        reg = match(r'^(\D+)(\d+)$', kw)
        query = Q()
        if reg:
            kw_alph = reg.group(1)
            kw_num = reg.group(2)
            query = query_use_type_version_factory(kw_alph, kw_num)

        return query

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
    first_g_kw = True # first group of kw
    first_g = True # first group
    while True: # loop infinitely
        # kw loading
        kw = keywords_splitted[i]
        print kw
        
        # query
        if first_g: # first group and very first kw
            gkw = kw
            query = query_factory(gkw)
            query_use_type = query_use_type_unspaced_factory(gkw)
            gkw_musics = Music.objects.filter(query | query_use_type)

        else:
            if first_g_kw: # first kw of any other group
                gkw = kw
                query_use_type = query_use_type_unspaced_factory(gkw)

            else: # any other kw of any other group
                gkw += ' ' + kw
                query_use_type = query_use_type_spaced_factory(gkw)
            
            query = query_factory(gkw)
            gkw_musics = gkw_musics.filter(query | query_use_type) # unlike very first kw, each gkw query filters previous results

        print gkw

        # check matching
        if gkw_musics: # if musics remain, let's save and continue
            latest_gkw_musics = gkw_musics
            new_result = {
                    'gkw': gkw,
                    'musics': gkw_musics,
                    }

            # first group kw or not?
            if first_g_kw: # if first group kw, let's down the flag and new save
                results.append(new_result)
                first_g_kw = False

            else: # else, nothing but update save
                results[-1] = new_result

            # if matching sucessfull, let's continue with another kw
            if keywords_amount - 1 == i: # if last kw processed, end of operation
                break

            else: # else continue
                i += 1
            
        else: # if no music remains
            if first_g: # first kw havn't a solely result, abort process
                break

            else: # restore previous sucessful set of results
                gkw_musics = latest_gkw_musics 

            if first_g_kw: # if no music detected for this single kw, assume kw is invalid and continue
                unmatched_kw.append(kw)
                if keywords_amount - 1 == i: # if last kw processed, end of operation
                    break

                else: # else continue
                    i += 1

            else: # previous group sucessfull, let's start a new group and analyse this kw again (no i incrementation)
                first_g_kw = True

        if first_g:
            first_g = False

    if results: # if at least one music has been found
        #musics = list(set(chain.from_iterable(
        #    [result['musics'] for result in results]
        #    )))
        gkw_musics = gkw_musics.order_by('item__itemname__name', 'item__itemname__name_origin', 'version')
        musics = list(set(gkw_musics))

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


            


