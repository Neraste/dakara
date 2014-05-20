from django.conf.urls import url

from music import views
from music.models import *

multi_edit_models = [Language, Role, MusicOpusType, OpusType, VideoType]
people_models = [Artist, Timer]

make_name_lower = lambda class_object: class_object.__name__.lower()



# Specific URLs
urlpatterns = []

# Generic URLs
for mod in multi_edit_models:
    obj = make_name_lower(mod)
    objects = obj + 's'
    urlpatterns.append( url( r'^' + objects + r'/$' , views.multi_edit , {'Model' : mod }, name = objects + "_edit" ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , views.multi_delete , {'Model' : mod }, name = obj + "_del"  ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/merge/$' , views.multi_merge , {'Model' : mod }, name = obj + "_merge" ) )

for mod in people_models:
    objects = make_name_lower(mod) + 's'
    urlpatterns.append( url( r'^' + objects + r'/$' , views.people_list , {'Model' : mod }, name = objects ) )
    urlpatterns.append( url( r'^' + objects + r'/new$' , views.people_new , {'Model' : mod }, name = objects + '_new' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , views.people_detail_delete , {'Model' : mod }, name = objects + '_detail_delete' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/edit/$' , views.people_edit , {'Model' : mod }, name = objects + '_edit' ) )


