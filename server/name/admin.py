from django.contrib import admin
from name.models import *
from name.forms import *

# Person name

class PersonNameInline(admin.StackedInline):
    model = PersonName
    extra = 1
    formset = NameInlineFormSet

class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonNameInline]

# Item name

class ItemNameInline(admin.TabularInline):
    model = ItemName
    extra = 1
    formset = NameInlineFormSet

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemNameInline]
