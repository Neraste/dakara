from django.db import models
from django.core.exceptions import ValidationError

class Language(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

#Names structures

def nameValidation(generalName):
    # Name model validation
    if not (generalName.name or generalName.nameTransliterated):
        raise ValidationError('One name or transliterated name needed')
    
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    
    @property
    def mainName(self):
        mainNames = self.itemname_set.filter(isMain=True)
        return mainNames[0] if mainNames else None
    
    def __unicode__(self):
        mainName = self.mainName
        return unicode(mainName) if mainName else unicode("No name")

class ItemName(models.Model):
    container = models.ForeignKey(Item)
    name = models.CharField(max_length = 200, blank = True)
    nameTransliterated = models.CharField(max_length = 200, blank = True)
    isMain = models.BooleanField()
    
    def __unicode__(self):
        return self.name if self.name else self.nameTransliterated
    
    def clean(self):
        nameValidation(self)

class Person(models.Model):
    id = models.AutoField(primary_key=True)    
    
    @property
    def mainName(self):
        mainNames = self.personname_set.filter(isMain=True)
        return mainNames[0] if mainNames else None
    
    def __unicode__(self):
        mainName = self.mainName
        return unicode(mainName) if mainName else unicode("No name")
        
        
class PersonName(models.Model):
    person = models.ForeignKey(Person)
    name = models.CharField(max_length = 200, blank = True)
    nameTransliterated = models.CharField(max_length = 200, blank = True)
    surname = models.CharField(max_length=200, blank = True)
    surnameTransliterated = models.CharField(max_length = 200, blank = True)
    isMain = models.BooleanField()
    
    def __unicode__(self):
        return self.name if self.name else self.nameTransliterated
    
    def clean(self):
        nameValidation(self)
    
#Artist related models

class Artist(models.Model):
    person = models.OneToOneField(Person)
    
    def __unicode__(self):
        return unicode(self.person)

class Role(models.Model):
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return self.name
    
#Opus (work, media, fiction) related models

class OpusType(models.Model):
    name = models.CharField(max_length=200)
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return self.name
    
class Opus(models.Model):
    item = models.OneToOneField(Item) # means an item name container
    language = models.ForeignKey(Language)
    date = models.DateField(null=True,blank=True)
    opusType = models.ForeignKey(OpusType)
    
    def __unicode__(self):
        return unicode(self.item)
    
class MusicOpusType(models.Model):
    nameShort = models.CharField(max_length=200)
    nameLong = models.CharField(max_length=200)
    hasVersion = models.BooleanField()
    hasInterval = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return self.nameLong

    
#Music model

class Music(models.Model):
    titleContainer = models.OneToOneField(Item)
    uses = models.ManyToManyField(Opus,through='MusicOpus')
    version = models.CharField(max_length=200,blank=True)
    isShort = models.BooleanField()
    isRemix = models.BooleanField()
    isCover = models.BooleanField()
    date = models.DateField(null=True,blank=True)
    duration = models.IntegerField()
    artists = models.ManyToManyField(Artist,through='ArtistMusic')
    languages = models.ManyToManyField(Language)
    note = models.TextField(blank=True)
    filePath = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.titleContainer)
    
    
#Video file Streams related models
class VideoType(models.Model):
    name = models.CharField(max_length=200)
    hasOpus = models.BooleanField()
    comment = models.CharField(max_length = 200, blank = True)
    
    def __unicode__(self):
        return self.name
    
class Video(models.Model):
    music = models.ForeignKey(Music)
    realisator = models.CharField(max_length = 200, blank = True)
    thumbnailPath = models.CharField(max_length = 200, blank = True)
    videoType = models.ForeignKey(VideoType, null = True, blank = True)
    opus = models.ForeignKey(Opus, null = True, blank = True, default = None)
    description = models.CharField(max_length = 200, blank = True)
    channelId = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return self.description

class Audio(models.Model):
    music = models.ForeignKey(Music)
    isInstrumental = models.BooleanField()
    description = models.CharField(max_length=200,blank=True)
    channelId = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return self.description
    
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
    filePath = models.CharField(max_length=200)

    def __unicode__(self):
        return self.description



    
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
    useType = models.ForeignKey(MusicOpusType) # could be musicOpusType, but it's longer, and Use means MusicOpus
    version = models.IntegerField(null=True, blank=True, default = None)
    interval = models.CharField(max_length=200,blank=True)
    language = models.ForeignKey(Language,null=True, blank=True, default = None) #null when opus original language
    kind = models.IntegerField(choices=MUSIC_OPUS_KIND)

