from django.conf.urls import url

from music import views
from music.models import *

multi_models = [Language, Role, MusicOpusType, OpusType, VideoType]
single_models = [Artist, Opus]

make_name_lower = lambda class_object: class_object.__name__.lower()



# Specific URLs
urlpatterns = []

# Generic URLs
for mod in multi_models:
    obj = make_name_lower(mod)
    objects = obj + 's'
    urlpatterns.append( url( r'^' + objects + r'/$' , views.multi_edit , {'Model' : mod }, name = objects + "_edit" ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , views.multi_delete , {'Model' : mod }, name = obj + "_del"  ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/merge/$' , views.multi_merge , {'Model' : mod }, name = obj + "_merge" ) )

for mod in single_models:
    obj = make_name_lower(mod)
    objects = obj + 's'
    function = 'music.views.' + obj
    urlpatterns.append( url( r'^' + objects + r'/$' , 'music.views.single_list' , {'Model' : mod }, name = obj + '_list' ) )
    urlpatterns.append( url( r'^' + objects + r'/new/$' , function + '_new' , name = obj + '_new' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , function + '_detail_delete' , name = obj + '_detail_delete' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/edit/$' , function + '_edit' , name = obj + '_edit' ) )


