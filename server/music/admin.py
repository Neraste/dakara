from django.contrib import admin
from music.models import *
from music.forms import *
from django.utils.functional import curry
# Register your models here.


#Name models


class PersonNameInline(admin.StackedInline):
    model = PersonName
    extra = 1
    formset = NameInlineFormSet

class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonNameInline]

admin.site.register(Person, PersonAdmin)

class ItemNameInline(admin.TabularInline):
    model = ItemName
    extra = 1
    formset = NameInlineFormSet

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
    formset = StreamInlineFormset
    
    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET":
            initial.append({
                'channelId': 0,
            })
        formset = super(VideoInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset
    
class AudioInline(admin.TabularInline):
    model = Audio
    extra = 1
    formset = StreamInlineFormset
    
    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET":
            initial.append({
                'channelId': 0,
            })
        formset = super(AudioInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset
    
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
