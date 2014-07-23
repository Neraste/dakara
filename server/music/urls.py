from django.conf.urls import url

from music import views
from music.models import *

from utils import get_name

multi_models = [Language, Role, MusicOpusType, OpusType, VideoType]
single_models = [Artist, Opus, Music]

urlpatterns = []


# Generic URLs
for mod in multi_models:
    obj = get_name(mod)
    objects = get_name(mod, plural = True)
    urlpatterns.extend([
        url( r'^' + objects + r'/$' , views.multi_edit , {'Model' : mod }, name = objects + "_edit" ),
        url( r'^' + objects + r'/(?P<id>\d+)/$' , views.multi_delete , {'Model' : mod }, name = obj + "_del"  ),
        url( r'^' + objects + r'/(?P<id>\d+)/merge/$' , views.multi_merge , {'Model' : mod }, name = obj + "_merge" ),
        ])

for mod in single_models:
    obj = get_name(mod)
    objects = get_name(mod, plural = True)
    function = 'music.views.' + obj
    urlpatterns.extend([
        url( r'^' + objects + r'/$' , function + '_list' , name = objects + '_list' ),
        url( r'^' + objects + r'/new/$' , function + '_new' , name = obj + '_new' ),
        url( r'^' + objects + r'/delete/$' , function + '_delete' , name = obj + '_delete' ),
        url( r'^' + objects + r'/merge/$' , function + '_merge' , name = obj + '_merge' ),
        url( r'^' + objects + r'/(?P<id>\d+)/$' , function + '_detail' , name = obj + '_detail' ),
        url( r'^' + objects + r'/(?P<id>\d+)/edit/$' , function + '_edit' , name = obj + '_edit' ),
        url( r'^' + objects + r'/search.*$' , function + '_search' , name = obj + '_search' ),
        ])


# Specific URLs
urlpatterns.extend([
        url(r'^search/.*$', 'music.views.global_search', name = 'music_global_search'),
        url(r'^advanced-search/.*$', 'music.views.advanced_search', name = 'music_advanced_search'),
        url(r'^' + get_name(Opus, plural = True) + '/type/(?P<opus_type>.+)/$', 'music.views.opus_list', name = get_name(Opus, plural = True) + '_list_type'),
        ])
