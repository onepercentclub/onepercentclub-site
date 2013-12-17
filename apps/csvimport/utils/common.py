""" Common utils. """

def has_duplicate_items(ls):
    """ Returns True when an iterable has duplicate items. """

    seen = set()

    for item in ls:
        if item in seen:
            return True

        seen.add(item)

    return False
