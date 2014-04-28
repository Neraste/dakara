from django.db import models
from django.core.exceptions import ValidationError

class Language(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name

#Names structures
    
class ObjectNameContainer(models.Model):
    id = models.AutoField(primary_key=True)
    
    @property
    def mainName(self):
        mainNames = self.objectname_set.filter(isMain=True)
        return mainNames[0] if mainNames else None
    
    def __unicode__(self):
        mainName = self.mainName
        return unicode(mainName) if mainName else unicode("")

class ObjectName(models.Model):
    container = models.ForeignKey(ObjectNameContainer)
    name = models.CharField(max_length=200)
    nameTransliterated = models.CharField(max_length=200,blank=True)
    isMain = models.BooleanField()
    
    def __unicode__(self):
        return self.name

class PersonNameContainer(models.Model):
    id = models.AutoField(primary_key=True)    
    
    @property
    def mainName(self):
        main_names = self.personname_set.filter(isMain=True)
        return main_names[0] if main_names else None
    
    def __unicode__(self):
        main_name = self.mainName
        return unicode(main_name) if main_name else unicode("")
        
        
class PersonName(models.Model):
    container = models.ForeignKey(PersonNameContainer)
    name = models.CharField(max_length=200)
    nameTransliterated = models.CharField(max_length=200,blank=True)
    surname = models.CharField(max_length=200,blank=True)
    surnameTransliterated = models.CharField(max_length=200,blank=True)
    isMain = models.BooleanField()
    
    def __unicode__(self):
        return self.name + " " + self.surname
    
#Artist related models

class Artist(models.Model):
    nameContainer = models.OneToOneField(PersonNameContainer)
    
    def __unicode__(self):
        return unicode(self.nameContainer)

class Role(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
#Opus (work, media, fiction) related models
    
class Opus(models.Model):
    nameContainer = models.OneToOneField(ObjectNameContainer)
    language = models.ForeignKey(Language)
    date = models.DateField(null=True,blank=True)
    
    def __unicode__(self):
        return unicode(self.nameContainer)
    
class MusicOpusType(models.Model):
    nameShort = models.CharField(max_length=200)
    nameLong = models.CharField(max_length=200)
    hasVersion = models.BooleanField()
    hasInterval = models.BooleanField()
    
    def __unicode__(self):
        return self.nameLong
    
#Music model

class Music(models.Model):
    titleContainer = models.OneToOneField(ObjectNameContainer)
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
    
    def __unicode__(self):
        return self.name
    
class Video(models.Model):
    music = models.ForeignKey(Music)
    realisator = models.CharField(max_length=200,blank=True)
    thumbnailPath = models.CharField(max_length=200,blank=True)
    type = models.ForeignKey(VideoType)
    opus = models.ForeignKey(Opus,null=True, blank=True, default = None)
    description = models.CharField(max_length=200,blank=True)
    channelId = models.IntegerField()
    
    def __unicode__(self):
        return self.description

class Audio(models.Model):
    music = models.ForeignKey(Music)
    isInstrumental = models.BooleanField()
    description = models.CharField(max_length=200,blank=True)
    channelId = models.IntegerField()
    
    def __unicode__(self):
        return self.description
    
class Timer(models.Model):
    nameContainer = models.OneToOneField(PersonNameContainer)
    
    def __unicode__(self):
        return unicode(self.nameContainer)

class Subtitle(models.Model):
    music = models.ForeignKey(Music)
    lyrics = models.TextField(blank=True)
    timer = models.ForeignKey(Timer,null=True, blank=True, default = None)
    transliteration = models.CharField(max_length=200,blank=True)
    description = models.CharField(max_length=200,blank=True)
#Transformer en channelId si on remuxe les fichiers a l'import
    filePath = models.CharField(max_length=200)
#  public String cleanLyrics(String inputLyrics)

    def __unicode__(self):
        return self.description



    
#Intermediary tables for many-to-many relations    
class ArtistMusic(models.Model):
    music = models.ForeignKey(Music)
    artist = models.ForeignKey(Artist)
    role = models.ForeignKey(Role)
 
class MusicOpus(models.Model):
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
    type = models.ForeignKey(MusicOpusType)
    version = models.IntegerField(null=True, blank=True, default = None)
    interval = models.CharField(max_length=200,blank=True)
    language = models.ForeignKey(Language,null=True, blank=True, default = None) #null when opus original language
    kind = models.IntegerField(choices=MUSIC_OPUS_KIND)

