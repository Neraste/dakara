from django.conf.urls import url

from music import views
from music.models import *

urlpatterns = [
    url(r'^languages/$', views.multiEdit, {'Model': Language} ),
    url(r'^roles/$', views.multiEdit, {'Model': Role} ),
    url(r'^usetypes/$', views.multiEdit, {'Model': MusicOpusType} ),
    url(r'^opustypes/$', views.multiEdit, {'Model': OpusType} ),
    url(r'^videotypes/$', views.multiEdit, {'Model': VideoType} ),
]

