from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from singer.models import *
from singer.forms import *
from music.views import music_list_processor

from utils import *

# Singer area #################################################################

def singer_list(request):
    '''List all singers'''
    singers = Singer.objects.all()
    singers_processed = singer_list_processor(singers)

    c = {
            'singers': singers_processed,
            'object_class': get_name(Singer),
            }
    
    return render(request, 'singer/list.html', c)

def singer_new_minimal(request):
    '''Create a minimal new user'''
    if request.method == 'POST':
        singer_new_minimal_form = SingerNewMinimalForm(request.POST)
        if singer_new_minimal_form.is_valid():
            singer_new_minimal_form.save()
            messages.success(request, 'User sucessfully created')
            
            return HttpResponseRedirect(reverse(get_name(Singer, plural = True) + '_list'))
            
        else:
            messages.error(request, 'Please check fields')

    else:
        singer_new_minimal_form = SingerNewMinimalForm()

    c = {
            'form': singer_new_minimal_form,
            }
            
    return render(request, 'singer/new.html', c)

def singer_detail(request, id):
    '''Display a singer profile'''
    singer = get_object_or_404(Singer, pk = id)
    main_name = singer.person.main_name if singer.person else None
    username = singer.username
    other_names = singer.person.other_names if singer.person else None
    favourites = singer.musicsinger_set.all()
    favourites_processed = favourite_list_processor(favourites)
    
    c = {
            'singer': singer,
            'main_name': main_name,
            'username': username,
            'other_names': other_names,
            'favourites': favourites_processed,
            }

    return render(request, 'singer/detail.html', c)
    

def singer_edit(request, id):
    pass

def singer_search(request):
    pass

def singer_list_processor(singers):
    '''process singers to be displayed as a sortened list with the following display:
        - id;
        - main_name,
        - username'''
    singers_list = singer_sort(singers)
    singers_processed = [{
        'id': singer.id,
        'main_name': singer.person.main_name if singer.person else None,
        'username': singer.username,
        } for singer in singers_list]
    
    return singers_processed

# Favourite area ##############################################################

def favourite_list(request):
    pass

def favourite_add(request, id):
    pass

def favourite_edit(request, id):
    pass

def favourite_remove(request, id):
    pass

def favourite_list_processor(favourites):
    '''Processes favourites to be displayed as a sorten list with following structure:
    - id,
    - grade,
    - music:
        + music_list_processor structure'''
    favourites_sort = list(favourites)
    favourites_sort.sort(key = lambda f: (
        f.music.item.main_name.name.lower(),
        f.music.item.main_name.name_origin.lower(),
        ))
    favourites_processed = [{
        'id': favourite.id,
        'grade': favourite.grade,
        'music': music_list_processor(favourite.music, sort = False),
        } for favourite in favourites]

    return favourites_processed

