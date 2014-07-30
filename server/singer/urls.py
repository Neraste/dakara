from django.conf.urls import url
from django.contrib.auth import views as auth_views

from singer import views

urlpatterns = [
    url(r'^new/$', views.singer_new_minimal, name = 'user_new'),
    url(r'^(?P<id>\d+)/$', views.singer_detail, name = 'user_detail'),
    url(r'^(?P<id>\d+)/edit/$', views.singer_edit, name = 'user_edit'),
    url(r'^search/$', views.singer_search, name = 'user_search'),
    url(r'^login/$', auth_views.login, name = 'user_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name = 'user_login'),

    url(r'^$', views.singer_list, name = 'users_list'),
    ]
