from django.utils.text import slugify

def get_related(obj):
    has_related = False
    related = {}
    for rel in obj._meta.get_all_related_objects():
        objects = getattr(obj, rel.get_accessor_name() ).all()
        if len(objects) != 0:
            has_related = True
        related[rel] = objects 
    for rel in obj._meta.get_all_related_many_to_many_objects():
        objects = getattr(obj, rel.get_accessor_name() ).all()
        if len(objects) != 0:
            has_related = True
        related[rel] = objects 
    return related if has_related else None

def get_name(Model, plural = False):
    '''Return an unicode slugified model verbose name if any or lowered model class name
    Warning: uses _meta attribute'''
    
    if not plural:
        name = Model._meta.verbose_name or Model.__name__.lower()
    
    else:
        name = Model._meta.verbose_name_plural or Model.__name__.lower() + 's'

    name = slugify(unicode(name))
    return name
