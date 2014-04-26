from django.contrib import admin
from music.models import *
# Register your models here.
admin.site.register(Language)
admin.site.register(Artist)
admin.site.register(Role)
admin.site.register(Opus)
admin.site.register(MusicOpusType)
admin.site.register(Music)
admin.site.register(VideoType)
admin.site.register(Timer)