from django.contrib import admin

from music.models import *
from music.forms import *
from name.admin import *

#Name models call

#admin.site.register(Person, PersonAdmin)
#admin.site.register(Item, ItemAdmin)    

#Music model

class ArtistMusicInline(admin.TabularInline):
    model = ArtistMusic
    extra = 1
    
class MusicOpusInline(admin.TabularInline):
    model = MusicOpus
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    formset = StreamInlineFormSet
    
class AudioInline(admin.TabularInline):
    model = Audio
    extra = 1
    formset = StreamInlineFormSet
    
class SubtitleInline(admin.StackedInline):
    model = Subtitle
    extra = 1
    
class MusicAdmin(admin.ModelAdmin):
    inlines = (ArtistMusicInline,MusicOpusInline,VideoInline,AudioInline,SubtitleInline)

admin.site.register(Music, MusicAdmin)
admin.site.register(Artist)
admin.site.register(Language)
admin.site.register(Role)
admin.site.register(Opus)
admin.site.register(MusicOpusType)
admin.site.register(VideoType)
admin.site.register(Timer)
admin.site.register(OpusType)
