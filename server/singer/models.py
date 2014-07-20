from django.db import models
from django.contrib.auth.models import AbstractUser

from music.models import Music
from name.models import *

class Singer(AbstractUser):
    person = models.OneToOneField(Person, null = True, blank = True)
    favourites = models.ManyToManyField(Music, through = 'MusicSinger')

    def __unicode__(self):
        return unicode(self.person) if self.person else self.username

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

class MusicSinger(models.Model):
    singer = models.ForeignKey(Singer)
    music = models.ForeignKey(Music)
    grade = models.PositiveSmallIntegerField(null = True, blank = True)
    
    class Meta:
        verbose_name = "favourite"
        verbose_name_plural = "favourites"
