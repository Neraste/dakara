from django.conf.urls import url

from singer import views

urlpatterns = [
    url(r'^/$', 'singer_list', name = 'users_list'),
    url(r'^new/$', 'singer_new', name = 'user_new'),
    url(r'^(?P<id>\d+)/$', 'singer_detail_delete', name = 'user_detail_delete'),
    url(r'^(?P<id>\d+)/edit/$', 'singer_edit', name = 'user_edit'),
    url(r'^search/$', 'singer_search', name = 'user_search'),
    ]
