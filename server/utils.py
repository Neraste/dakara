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
