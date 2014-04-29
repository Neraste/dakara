from django.contrib import admin
from music.models import *
from music.forms import *
# Register your models here.


#Name models


class PersonNameInline(admin.StackedInline):
    model = PersonName
    extra = 1
    formset = NameInlineFormset

class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonNameInline]

admin.site.register(Person, PersonAdmin)

class ItemNameInline(admin.TabularInline):
    model = ItemName
    extra = 1
    formset = NameInlineFormset

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemNameInline]

admin.site.register(Item, ItemAdmin)    


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
    
class AudioInline(admin.TabularInline):
    model = Audio
    extra = 1
    
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
