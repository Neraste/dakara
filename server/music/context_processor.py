from music.models import *

def opus_types(request):
    '''Give all opus types'''
    opus_types = OpusType.objects.all()
    context = {
            'opus_types_list': opus_types
            }

    return context
