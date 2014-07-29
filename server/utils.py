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

def convert_query_set_to_list(query_set):
    '''Try to convert a query set to a list, give nothing silently if failed'''
    try:
        query_set_list = list(query_set)

    except:
        print("ERROR: query set conversion to list failed")
        query_set_list = []

    return query_set_list


def person_sort(query_set):
    '''Return a sorten list of objetcs using a person attribute'''
    query_set_list = convert_query_set_to_list(query_set)

    query_set_list.sort(key = lambda a: (
        a.person.main_name.name.lower(),
        a.person.main_name.surname.lower(),
        a.person.main_name.name_origin.lower(),
        a.person.main_name.surname_origin.lower(),
        ))

    return query_set_list

def singer_sort(query_set):
    '''Return a sorten list of singers using a person attribute or basic username'''
    query_set_list = convert_query_set_to_list(query_set)

    query_set_list.sort(key = lambda a: (
        a.person.main_name.name.lower(),
        a.person.main_name.surname.lower(),
        a.person.main_name.name_origin.lower(),
        a.person.main_name.surname_origin.lower(),
        ) if a.person else (
            a.email.lower()
            )
        )

    return query_set_list

def item_sort(query_set):
    '''Return a sorten list of objects using a item attribute'''
    query_set_list = convert_query_set_to_list(query_set)

    query_set_list.sort(key = lambda a: (
        a.item.main_name.name.lower(),
        a.item.main_name.name_origin.lower(),
        ))

    return query_set_list
