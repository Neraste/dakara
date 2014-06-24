from django.db import models
from django.contrib.auth.models import AbstractUser
from music.models import Music

class Singer(AbstractUser):
    favourites = models.ManyToManyField(Music, through = 'MusicSinger')

    class Meta:
        verbose_name = "singer"
        verbose_name_plural = "singers"

class MusicSinger(models.Model):
    singer = models.ForeignKey(Singer)
    music = models.ForeignKey(Music)
    grade = models.IntegerField()
    
    class Meta:
        verbose_name = "favourite"
        verbose_name_plural = "favourites"
