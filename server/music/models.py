from django.db import models
from django.core.exceptions import ValidationError

from autoslug import AutoSlugField

from name.models import *

class Language(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
#Artist related models

class Artist(models.Model):
    person = models.OneToOneField(Person)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return unicode(self.person)
    
    @property
    def main_name(self):
        return self.person.main_name

    @property
    def other_names(self):
        return self.person.other_names

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
    name_slug = AutoSlugField(populate_from = 'name', always_update = True, unique = True)

    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")

    class Meta:
        verbose_name = "opus type"
        verbose_name_plural = "opus types"
    
class Opus(models.Model):
    item = models.OneToOneField(Item) # means an item name container
    language = models.ForeignKey(Language,on_delete=models.PROTECT)
    date = models.PositiveSmallIntegerField(null = True, blank = True)
    opus_type = models.ForeignKey(OpusType,on_delete=models.PROTECT)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return unicode(self.item)
    
    @property
    def main_name(self):
        return self.item.main_name

    @property
    def other_names(self):
        return self.item.other_names

    class Meta:
        verbose_name = "opus"
        verbose_name_plural = "opuses"
    
class MusicOpusType(models.Model): # aka use type
    name_short = models.CharField(max_length=5)
    name_long = models.CharField(max_length=200)
    has_version = models.BooleanField()
    has_interval = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name_long) if self.name_long else unicode("No name")

    class Meta:
        verbose_name = "use type"
        verbose_name_plural = "use types"

    def clean(self):
        if len(self.name_short.split()) > 1:
            raise ValidationError("Short name mustn't have space")
    
#Music model

class Music(models.Model):
    item = models.OneToOneField(Item)
    uses = models.ManyToManyField(Opus,through='MusicOpus')
    version = models.CharField(max_length=200,blank=True)
    is_short = models.BooleanField()
    is_remix = models.BooleanField()
    is_cover = models.BooleanField()
    date = models.PositiveSmallIntegerField(null = True, blank = True)
    duration = models.PositiveIntegerField()
    artists = models.ManyToManyField(Artist,through='ArtistMusic')
    languages = models.ManyToManyField(Language)
    note = models.TextField(blank=True)
    file_path = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.item)
    
    @property
    def main_name(self):
        return self.item.main_name

    @property
    def other_names(self):
        return self.item.other_names

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
    channel_id = models.PositiveSmallIntegerField()
    
    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")

    class Meta:
        verbose_name = "video stream"
        verbose_name_plural = "video streams"

class Audio(models.Model):
    music = models.ForeignKey(Music)
    is_instrumental = models.BooleanField()
    description = models.CharField(max_length=200,blank=True)
    channel_id = models.PositiveSmallIntegerField()
    
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
    #timer = models.ForeignKey(Timer,null=True, blank=True, default = None,on_delete=models.SET_NULL)
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
    artist = models.ForeignKey(Artist)
    roles = models.ManyToManyField(Role)

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
    use_type = models.ForeignKey(MusicOpusType,on_delete=models.PROTECT) # could be musicOpusType, but it's longer, and Use means MusicOpus
    version = models.IntegerField(null=True, blank=True, default = None)
    interval = models.CharField(max_length=200,blank=True)
    language = models.ForeignKey(Language,null=True, blank=True, default = None,on_delete=models.PROTECT) #null when opus original language
    kind = models.PositiveSmallIntegerField(choices=MUSIC_OPUS_KIND)

    def get_linked(self):
        res = {'main': self.music, 'sec' : self.opus}
        return res

    class Meta:
        verbose_name = "use"
        verbose_name_plural = "uses"
