from django.conf.urls import url

from singer import views

urlpatterns = [
    url(r'^new/$', views.singer_new_minimal, name = 'user_new'),
    url(r'^(?P<id>\d+)/$', views.singer_detail_delete, name = 'user_detail_delete'),
    url(r'^(?P<id>\d+)/edit/$', views.singer_edit, name = 'user_edit'),
    url(r'^search/$', views.singer_search, name = 'user_search'),
    url(r'^$', views.singer_list, name = 'users_list'),
    ]
