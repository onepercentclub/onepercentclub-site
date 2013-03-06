

def get_client_ip(request):
    """ A utility method that returns the client IP for the given request. """

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def set_author_editor_ip(request, obj):
    """ A utility method to set the author, editor and IP address on an object based on information in a request. """

    if not hasattr(obj, 'author'):
        obj.author = request.user
    else:
        obj.editor = request.user
    obj.ip_address = get_client_ip(request)
