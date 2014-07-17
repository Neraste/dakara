from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from singer.models import *
from singer.forms import *

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
    pass

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
