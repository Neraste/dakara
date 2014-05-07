from django.db import models
from django.core.exceptions import ValidationError

class Language(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

#Names structures

def name_validation(generalName):
    # Name model validation
    if not (generalName.name or generalName.name_transliterated):
        raise ValidationError('One name or transliterated name needed')
    
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
    name = models.CharField(max_length = 200, blank = True)
    name_transliterated = models.CharField(max_length = 200, blank = True)
    is_main = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode(self.name_transliterated)
    
    def clean(self):
        name_validation(self)

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
    name = models.CharField(max_length = 200, blank = True)
    name_transliterated = models.CharField(max_length = 200, blank = True)
    surname = models.CharField(max_length=200, blank = True)
    surname_transliterated = models.CharField(max_length = 200, blank = True)
    is_main = models.BooleanField()
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode(self.name_transliterated)
    
    def clean(self):
        name_validation(self)
    
#Artist related models

class Artist(models.Model):
    person = models.OneToOneField(Person)
    
    def __unicode__(self):
        return unicode(self.person)

class Role(models.Model):
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")
    
#Opus (work, media, fiction) related models

class OpusType(models.Model):
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")
    
class Opus(models.Model):
    item = models.OneToOneField(Item) # means an item name container
    language = models.ForeignKey(Language)
    date = models.DateField(null=True,blank=True)
    opus_type = models.ForeignKey(OpusType)
    
    def __unicode__(self):
        return unicode(self.item)
    
class MusicOpusType(models.Model):
    name_short = models.CharField(max_length=200)
    name_long = models.CharField(max_length=200)
    has_version = models.BooleanField()
    has_interval = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name_long) if self.name_long else unicode("No name")

    
#Music model

class Music(models.Model):
    item = models.OneToOneField(Item)
    uses = models.ManyToManyField(Opus,through='MusicOpus')
    version = models.CharField(max_length=200,blank=True)
    is_short = models.BooleanField()
    is_remix = models.BooleanField()
    is_cover = models.BooleanField()
    date = models.DateField(null=True,blank=True)
    duration = models.IntegerField()
    artists = models.ManyToManyField(Artist,through='ArtistMusic')
    languages = models.ManyToManyField(Language)
    note = models.TextField(blank=True)
    file_path = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.item)
    
    
#Video file Streams related models
class VideoType(models.Model):
    name = models.CharField(max_length=200)
    has_opus = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return unicode(self.name) if self.name else unicode("No name")
    
class Video(models.Model):
    music = models.ForeignKey(Music)
    realisator = models.CharField(max_length = 200, blank = True)
    thumbnail_path = models.CharField(max_length = 200, blank = True)
    video_type = models.ForeignKey(VideoType, null = True, blank = True)
    opus = models.ForeignKey(Opus, null = True, blank = True, default = None)
    description = models.CharField(max_length = 200, blank = True)
    channel_id = models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")

class Audio(models.Model):
    music = models.ForeignKey(Music)
    is_instrumental = models.BooleanField()
    description = models.CharField(max_length=200,blank=True)
    channel_id = models.IntegerField()
    
    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")
    
class Timer(models.Model):
    person = models.OneToOneField(Person)
    
    def __unicode__(self):
        return unicode(self.person)

class Subtitle(models.Model):
    music = models.ForeignKey(Music)
    lyrics = models.TextField(blank=True)
    timer = models.ForeignKey(Timer,null=True, blank=True, default = None)
    transliteration = models.CharField(max_length=200,blank=True)
    description = models.CharField(max_length=200,blank=True)
    file_path = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.description) if self.description else unicode("No description")



    
#Intermediary tables for many-to-many relations    
class ArtistMusic(models.Model):
    music = models.ForeignKey(Music)
    artist = models.ForeignKey(Artist)
    role = models.ForeignKey(Role)
 
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
    opus = models.ForeignKey(Opus)
    use_type = models.ForeignKey(MusicOpusType) # could be musicOpusType, but it's longer, and Use means MusicOpus
    version = models.IntegerField(null=True, blank=True, default = None)
    interval = models.CharField(max_length=200,blank=True)
    language = models.ForeignKey(Language,null=True, blank=True, default = None) #null when opus original language
    kind = models.IntegerField(choices=MUSIC_OPUS_KIND)

