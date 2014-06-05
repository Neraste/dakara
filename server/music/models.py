from django.db import models
import select2.fields
from django.core.exceptions import ValidationError
from django.db.models import Q

class Language(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

#Names structures

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    
    @property
    def main_name(self):
        main_names = self.itemname_set.filter(is_main=True)
        return main_names[0] if main_names else None
    
    def __unicode__(self):
        main_name = self.main_name
        return unicode(main_name) if main_name else unicode("No name")

class ItemName(models.Model):
    container = models.ForeignKey(Item)
    name = models.CharField(max_length = 200)
    name_origin = models.CharField(max_length = 200, blank = True)
    is_main = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode(self.name_origin)
    
class Person(models.Model):
    id = models.AutoField(primary_key=True)    
    
    @property
    def main_name(self):
        main_names = self.personname_set.filter(is_main=True)
        return main_names[0] if main_names else None
    
    def __unicode__(self):
        main_name = self.main_name
        return unicode(main_name) if main_name else unicode("No name")
        
        
class PersonName(models.Model):
    person = models.ForeignKey(Person)
    name = models.CharField(max_length = 200)
    name_origin = models.CharField(max_length = 200, blank = True)
    surname = models.CharField(max_length=200, blank = True)
    surname_origin = models.CharField(max_length = 200, blank = True)
    is_main = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode(self.name_origin)
    
#Artist related models

class Artist(models.Model):
    person = models.OneToOneField(Person)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return unicode(self.person)

    class Meta:
        verbose_name = "artist"
        verbose_name_plural = "artists"

class Role(models.Model):
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")

    class Meta:
        verbose_name = "role"
        verbose_name_plural = "roles"
    
#Opus (work, media, fiction) related models

class OpusType(models.Model):
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")

    class Meta:
        verbose_name = "opus type"
        verbose_name_plural = "opus types"
    
class Opus(models.Model):
    item = models.OneToOneField(Item) # means an item name container
    language = models.ForeignKey(Language,on_delete=models.PROTECT)
    date = models.IntegerField(null=True,blank=True)
    opus_type = models.ForeignKey(OpusType,on_delete=models.PROTECT)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return unicode(self.item)

    class Meta:
        verbose_name = "opus"
        verbose_name_plural = "opuses"
    
class MusicOpusType(models.Model):
    name_short = models.CharField(max_length=200)
    name_long = models.CharField(max_length=200)
    has_version = models.BooleanField()
    has_interval = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name_long) if self.name_long else unicode("No name")

    class Meta:
        verbose_name = "use type"
        verbose_name_plural = "use types"

    
#Music model

class Music(models.Model):
    item = models.OneToOneField(Item)
    uses = models.ManyToManyField(Opus,through='MusicOpus')
    version = models.CharField(max_length=200,blank=True)
    is_short = models.BooleanField()
    is_remix = models.BooleanField()
    is_cover = models.BooleanField()
    date = models.IntegerField(null=True,blank=True)
    duration = models.IntegerField()
    artists = models.ManyToManyField(Artist,through='ArtistMusic')
    languages  = select2.fields.ManyToManyField(Language,overlay="Select languages")
    note = models.TextField(blank=True)
    file_path = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.item)

    @property
    def main_artist(self):
        artists = self.artists.all()
        return artists[0] if artists else None
    
    @property
    def main_exact_use(self):
        exact_uses = self.musicopus_set.filter(kind = 1)
        return exact_uses[0] if exact_uses else None
    
    @property
    def has_instrumental(self):
        instrumental_audio = self.audio_set.filter(is_instrumental = True)
        return any(instrumental_audio)

    class Meta:
        verbose_name = "music"
        verbose_name_plural = "musics"
    
    
#Video file Streams related models
class VideoType(models.Model):
    name = models.CharField(max_length=200)
    has_opus = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")

    class Meta:
        verbose_name = "video type"
        verbose_name_plural = "video types"
    
class Video(models.Model):
    music = models.ForeignKey(Music)
    realisator = models.CharField(max_length = 200, blank = True)
    thumbnail_path = models.CharField(max_length = 200, blank = True)
    video_type = models.ForeignKey(VideoType, null = True, blank = True,on_delete=models.PROTECT)
    opus = models.ForeignKey(Opus, null = True, blank = True, default = None,on_delete=models.PROTECT)
    description = models.CharField(max_length = 200, blank = True)
    channel_id = models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")

    class Meta:
        verbose_name = "video stream"
        verbose_name_plural = "video streams"

class Audio(models.Model):
    music = models.ForeignKey(Music)
    is_instrumental = models.BooleanField()
    description = models.CharField(max_length=200,blank=True)
    channel_id = models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")

    class Meta:
        verbose_name = "audio stream"
        verbose_name_plural = "audio streams"
    
class Timer(models.Model):
    person = models.OneToOneField(Person)
    
    def __unicode__(self):
        return unicode(self.person)

class Subtitle(models.Model):
    music = models.ForeignKey(Music)
    lyrics = models.TextField(blank=True)
    timer = models.ForeignKey(Timer,null=True, blank=True, default = None,on_delete=models.SET_NULL)
    transliteration = models.CharField(max_length=200,blank=True)
    description = models.CharField(max_length=200,blank=True)
    file_path = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")

    class Meta:
        verbose_name = "subtitle stream"
        verbose_name_plural = "subtitle streams"



    
#Intermediary tables for many-to-many relations    
class ArtistMusic(models.Model):
    music = models.ForeignKey(Music)
    artist = select2.fields.ForeignKey(Artist,
        ajax=True,
        search_field= lambda s: Q(person__personname__name__contains=s) | Q(person__personname__name_origin__contains=s) | Q(person__personname__surname__contains=s) | Q(person__personname__surname_origin__contains=s),
        js_options={'minimumInputLength': 2},
        overlay = "Choose an artist")

    roles = select2.fields.ManyToManyField(Role,overlay="Select Roles")

    def get_linked(self):
        res = {'main': self.music, 'sec' : self.artist}
        return res

    class Meta:
        verbose_name = "artist"
        verbose_name_plural = "artists"
        
 
class MusicOpus(models.Model): # means Use
    EXACT = 1
    LINKED = 2
    UNLINKED = 3
    MUSIC_OPUS_KIND = (
        (EXACT, 'Exact'),
        (LINKED, 'Linked'),
        (UNLINKED, 'Unliked'),
    )

    music = models.ForeignKey(Music)
    opus = models.ForeignKey(Opus,on_delete=models.PROTECT)
    
    opus = select2.fields.ForeignKey(Opus,
        ajax=True,
        search_field= lambda s: Q(item__itemname__name__contains=s) | Q(item__itemname__name_origin__contains=s) ,
        js_options={'minimumInputLength': 2},
        overlay = "Choose an opus")

    use_type = models.ForeignKey(MusicOpusType,on_delete=models.PROTECT) # could be musicOpusType, but it's longer, and Use means MusicOpus
    version = models.IntegerField(null=True, blank=True, default = None)
    interval = models.CharField(max_length=200,blank=True)
    language = models.ForeignKey(Language,null=True, blank=True, default = None,on_delete=models.PROTECT) #null when opus original language
    kind = models.IntegerField(choices=MUSIC_OPUS_KIND)

    def get_linked(self):
        res = {'main': self.music, 'sec' : self.opus}
        return res

    class Meta:
        verbose_name = "use"
        verbose_name_plural = "uses"
