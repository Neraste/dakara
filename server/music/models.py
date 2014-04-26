from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=200)

#Names structures
    
class ObjectNameContainer(models.Model):
    id = models.AutoField(primary_key=True)

class ObjectName(models.Model):
    container = models.ForeignKey(ObjectNameContainer)
    name = models.CharField(max_length=200)
    nameTransliterated = models.CharField(max_length=200)
    isMain = models.BooleanField()

class PersonNameContainer(models.Model):
    id = models.AutoField(primary_key=True) 
    
class PersonName(models.Model):
    container = models.ForeignKey(PersonNameContainer)
    name = models.CharField(max_length=200)
    nameTransliterated = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    surnameTransliterated = models.CharField(max_length=200)
    isMain = models.BooleanField()
    
#Artist related models

class Artist(models.Model):
    nameContainer = models.OneToOneField(PersonNameContainer)

class Role(models.Model):
    name = models.CharField(max_length=200)
    
#Opus (work, media, fiction) related models
    
class Opus(models.Model):
    nameContainer = models.OneToOneField(ObjectNameContainer)
    language = models.ForeignKey(Language)
    date = models.DateField()
    
class MusicOpusType(models.Model):
    nameShort = models.CharField(max_length=200)
    nameLong = models.CharField(max_length=200)
    hasVersion = models.BooleanField()
    hasInterval = models.BooleanField()
    
#Music model

class Music(models.Model):
    titleContainer = models.OneToOneField(ObjectNameContainer)
    uses = models.ManyToManyField(Opus,through='MusicOpus')
    version = models.CharField(max_length=200)
    isShort = models.BooleanField()
    isRemix = models.BooleanField()
    isCover = models.BooleanField()
    date = models.DateField()
    duration = models.IntegerField()
    artists = models.ManyToManyField(Artist,through='ArtistMusic')
    languages = models.ManyToManyField(Language)
    note = models.TextField()
    filePath = models.CharField(max_length=200)
    
    
#Video file Streams related models
class VideoType(models.Model):
    name = models.CharField(max_length=200)
    hasOpus = models.BooleanField()
    
class Video(models.Model):
    music = models.ForeignKey(Music)
    realisator = models.CharField(max_length=200)
    thumbnailPath = models.CharField(max_length=200)
    type = models.ForeignKey(VideoType)
    opus = models.ForeignKey(Opus,null=True, blank=True, default = None)
    description = models.CharField(max_length=200)
    channelId = models.IntegerField()

class Audio(models.Model):
    music = models.ForeignKey(Music)
    isInstrumental = models.BooleanField()
    description = models.CharField(max_length=200)
    channelId = models.IntegerField()
    
class Timer(models.Model):
    nameContainer = models.OneToOneField(PersonNameContainer)

class Subtitle(models.Model):
    music = models.ForeignKey(Music)
    lyrics = models.TextField()
    timer = models.ForeignKey(Timer,null=True, blank=True, default = None)
    transliteration = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
#Transformer en channelId si on remuxe les fichiers ? l'import
    filePath = models.CharField(max_length=200)
#  public String cleanLyrics(String inputLyrics)



    
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
    interval = models.CharField(max_length=200)
    language = models.ForeignKey(Language,null=True, blank=True, default = None) #null when opus original language
    kind = models.IntegerField(choices=MUSIC_OPUS_KIND)

