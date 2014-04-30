from django.conf.urls import url

from music import views

urlpatterns = [
    url(r'^languages/$', views.langIndex, name='langIndex'),
    url(r'^languages/add$', views.langAdd, name='langAdd'),
    url(r'^languages/del/(?P<langId>\d+)/$', views.langDel, name='langDel'),
]

