from django.conf.urls import url

from music import views
from music.models import *

urlpatterns = [
    url(r'^languages/$', views.multi_edit, {'Model': Language} ),
    url(r'^roles/$', views.multi_edit, {'Model': Role} ),
    url(r'^usetypes/$', views.multi_edit, {'Model': MusicOpusType} ),
    url(r'^opustypes/$', views.multi_edit, {'Model': OpusType} ),
    url(r'^videotypes/$', views.multi_edit, {'Model': VideoType} ),
    url(r'^languages/(?P<id>\d+)/$', views.multi_delete, {'Model': Language} ),
    url(r'^roles/(?P<id>\d+)/$', views.multi_delete, {'Model': Role} ),
    url(r'^usetypes/(?P<id>\d+)/$', views.multi_delete, {'Model': MusicOpusType} ),
    url(r'^opustypes/(?P<id>\d+)/$', views.multi_delete, {'Model': OpusType} ),
    url(r'^videotypes/(?P<id>\d+)/$', views.multi_delete, {'Model': VideoType} ),
    url(r'^languages/(?P<id>\d+)/merge/$', views.multi_merge, {'Model': Language} ),
    url(r'^roles/(?P<id>\d+)/merge/$', views.multi_merge, {'Model': Role} ),
    url(r'^usetypes/(?P<id>\d+)/merge/$', views.multi_merge, {'Model': MusicOpusType} ),
    url(r'^opustypes/(?P<id>\d+)/merge/$', views.multi_merge, {'Model': OpusType} ),
    url(r'^videotypes/(?P<id>\d+)/merge/$', views.multi_merge, {'Model': VideoType} ),

]

