def get_related(obj):
    related = {}
    for rel in obj._meta.get_all_related_objects():
        objects = getattr(obj, rel.get_accessor_name() ).all()
        related[rel.var_name] = objects 
    for rel in obj._meta.get_all_related_many_to_many_objects():
        objects = getattr(obj, rel.get_accessor_name() ).all()
        related[rel.var_name] = objects 
    return related
