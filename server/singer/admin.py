from django.contrib import admin
from singer.models import *

class FavouriteInline(admin.TabularInline):
    model = MusicSinger
    extra = 1

class SingerAdmin(admin.ModelAdmin):
    inlines = [FavouriteInline]
    fields = ('username', 'password', 'email', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')

admin.site.register(Singer, SingerAdmin)
