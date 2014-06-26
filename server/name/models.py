from django.db import models

#Names structures

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    
    @property
    def main_name(self):
        main_names = self.itemname_set.filter(is_main = True)
        return main_names[0] if main_names else None
    
    @property
    def other_names(self):
        other_names = self.itemname_set.filter(is_main = False)
        return other_names
    
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
        main_names = self.personname_set.filter(is_main = True)
        return main_names[0] if main_names else None
    
    @property
    def other_names(self):
        other_names = self.personname_set.filter(is_main = False)
        return other_names
    
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
        return u"{} {}".format(self.name, self.surname) if self.surname else unicode(self.name)
