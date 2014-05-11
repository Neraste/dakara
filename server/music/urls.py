from django.conf.urls import url

from music import views
from music.models import *

multi_edit_models = [Language, Role, MusicOpusType, OpusType, VideoType]
people_models = [Artist, Timer]

make_name_lower = lambda class_object: class_object.__name__.lower()

urlpatterns = []

# Generic URLs
for mod in multi_edit_models:
    objects = make_name_lower(mod) + 's'
    urlpatterns.append( url( r'^' + objects + r'/$' , views.multi_edit , {'Model' : mod } ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , views.multi_delete , {'Model' : mod } ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/merge/$' , views.multi_merge , {'Model' : mod } ) )

for mod in people_models:
    objects = make_name_lower(mod) + 's'
    urlpatterns.append( url( r'^' + objects + r'/$' , views.people_list , {'Model' : mod } ) )
    urlpatterns.append( url( r'^' + objects + r'/new$' , views.people_new , {'Model' : mod } ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/edit/$' , views.people_edit , {'Model' : mod }, name = objects + '_edit' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/delete/$' , views.people_delete , {'Model' : mod } ) )

# Specific URLs

