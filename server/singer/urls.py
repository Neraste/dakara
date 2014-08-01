from django.conf.urls import url
from django.contrib.auth import views as auth_views

from singer import views

urlpatterns = [
    url(r'^users/new/$', views.singer_minimal_new, name = 'user_new'),
    url(r'^users/(?P<id>\d+)/$', views.singer_detail, name = 'user_detail'),
    url(r'^users/(?P<id>\d+)/edit/$', views.singer_edit, name = 'user_edit'),
    url(r'^users/search/$', views.singer_search, name = 'user_search'),
    url(r'^users/$', views.singer_list, name = 'users_list'),
    url(r'^login/$', auth_views.login, name = 'user_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name = 'user_login'),
    url(r'^profile/$', views.singer_profile, name = 'user_profile'),
    ]
