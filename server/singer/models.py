from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from music.models import Music
from name.models import *

class SingerManager(BaseUserManager):
    def create_user(self, email, password = None):
        '''Create a new user with email as identifier and password'''
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email = self.normalize_email(email))
        user.set_password(password)
        user.save(using = self._db)
        print "new singer created with create_user: {}".format(user)
        return user

    def create_superuser(self, email, password):
        '''Create a new superuser with email as identifier and password'''
        if not password:
            raise ValueError('Superuser must have a defined and non empty password')

        superuser = self.create_user(email, password)
        superuser.is_admin = True
        superuser.save(using = self._db)
        return superuser

class Singer(AbstractBaseUser):
    email = models.EmailField(unique = True)
    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default = False)
    person = models.OneToOneField(Person, null = True, blank = True)
    #favourites = models.ManyToManyField(Music, through = 'MusicSinger')

    objects = SingerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    def __unicode__(self):
        return unicode(self.person) if self.person else self.email

    def get_full_name(self):
        return self.person.main_name if self.person else None

    def get_short_name(self):
        return self.person.main_name.name if sel.person else self.email

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


#class MusicSinger(models.Model):
#    singer = models.ForeignKey(Singer)
#    music = models.ForeignKey(Music)
#    grade = models.PositiveSmallIntegerField(null = True, blank = True)
#    
#    class Meta:
#        verbose_name = "favourite"
#        verbose_name_plural = "favourites"
