from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory

from singer.models import *
from singer.forms import *
from music.views import music_list_processor
from name.models import *
from name.forms import *

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

def singer_minimal_new(request):
    '''Create a minimal new user'''
    if request.method == 'POST':
        singer_minimal_creation_form = SingerMinimalCreationForm(request.POST)
        if singer_minimal_creation_form.is_valid():
            singer = singer_minimal_creation_form.save(commit = False)
            name_splitted = singer.email.split('@')
            if name_splitted[0]:
                name_supposed = name_splitted[0]
                person = Person()
                person.save()
                person_name = PersonName(name = name_supposed, is_main = True, person = person)
                person_name.save()
                singer.person = person

            singer.save()
            messages.success(request, 'User sucessfully created')
            
            return HttpResponseRedirect(reverse(get_name(Singer, plural = True) + '_list'))
            
        else:
            messages.error(request, 'Please check fields')

    else:
        singer_minimal_creation_form = SingerMinimalCreationForm()

    c = {
            'form': singer_minimal_creation_form,
            }
            
    return render(request, 'singer/new.html', c)

def singer_edit(request, id):
    '''Edit an user'''
    singer = get_object_or_404(Singer, pk = id)
    person_flag = False if not singer.person else True # in case of singer created WITHOUT singer_minimal_new view, it has no person and thus a person shall be added

    person = singer.person if person_flag else Person() # singar can have a person or not
    NameFormSet = inlineformset_factory(Person, PersonName, formset = NameInlineFormSet, extra = 1, can_delete = True)
    if request.method == 'POST':
        singer_change_form = SingerChangeForm(request.POST, instance = singer)
        name_form_set = NameFormSet(request.POST, instance = person)
        if singer_change_form.is_valid() and name_form_set.is_valid():
            if not person_flag:
                person.save()
                name_form_set.save()
                singer = singer_change_form.save(commit = False)
                singer.person = person
                singer.save()

            else:
                name_form_set.save()
                singer_change_form.save()

            messages.success(request, "Singer sucessfully edited")
            
        else:
            messages.error(request, "Please check fields")
            

    else:
        singer_change_form = SingerChangeForm(instance = singer)
        name_form_set = NameFormSet(instance = person)

    c = {
            'form': singer_change_form,
            'name_form_set': name_form_set,
            }
    
    return render(request, 'singer/edit.html', c)

def singer_detail(request, id):
    '''Display a singer profile'''
    singer = get_object_or_404(Singer, pk = id)
    main_name = singer.person.main_name if singer.person else None
    email = singer.email
    other_names = singer.person.other_names if singer.person else None
    #favourites = singer.musicsinger_set.all()
    #favourites_processed = favourite_list_processor(favourites)
    
    c = {
            'singer': singer,
            'main_name': main_name,
            'username': email,
            'other_names': other_names,
            #'favourites': favourites_processed,
            }

    return render(request, 'singer/detail.html', c)

def singer_profile(request):
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
        'username': singer.email,
        } for singer in singers_list]
    
    return singers_processed

# Favourite area ##############################################################

#def favourite_list(request):
#    pass
#
#def favourite_add(request, id):
#    pass
#
#def favourite_edit(request, id):
#    pass
#
#def favourite_remove(request, id):
#    pass
#
#def favourite_list_processor(favourites):
#    '''Processes favourites to be displayed as a sorten list with following structure:
#    - id,
#    - grade,
#    - music:
#        + music_list_processor structure'''
#    favourites_sort = list(favourites)
#    favourites_sort.sort(key = lambda f: (
#        f.music.item.main_name.name.lower(),
#        f.music.item.main_name.name_origin.lower(),
#        ))
#    favourites_processed = [{
#        'id': favourite.id,
#        'grade': favourite.grade,
#        'music': music_list_processor(favourite.music, sort = False),
#        } for favourite in favourites]
#
#    return favourites_processed

