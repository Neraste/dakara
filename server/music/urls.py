from django.conf.urls import url

from music import views
from music.models import *

from utils import get_name

multi_models = [Language, Role, MusicOpusType, OpusType, VideoType]
single_models = [Artist, Opus]

# Specific URLs
urlpatterns = []

# Generic URLs
for mod in multi_models:
    obj = get_name(mod)
    objects = get_name(mod, plural = True)
    urlpatterns.append( url( r'^' + objects + r'/$' , views.multi_edit , {'Model' : mod }, name = objects + "_edit" ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , views.multi_delete , {'Model' : mod }, name = obj + "_del"  ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/merge/$' , views.multi_merge , {'Model' : mod }, name = obj + "_merge" ) )

for mod in single_models:
    obj = get_name(mod)
    objects = get_name(mod, plural = True)
    function = 'music.views.' + obj
    urlpatterns.append( url( r'^' + objects + r'/$' , function + '_list' , name = objects + '_list' ) )
    urlpatterns.append( url( r'^' + objects + r'/new/$' , function + '_new' , name = obj + '_new' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/$' , function + '_detail_delete' , name = obj + '_detail_delete' ) )
    urlpatterns.append( url( r'^' + objects + r'/(?P<id>\d+)/edit/$' , function + '_edit' , name = obj + '_edit' ) )
    urlpatterns.append( url( r'^' + objects + r'/search.*$' , function + '_search' , name = obj + '_search' ) )


