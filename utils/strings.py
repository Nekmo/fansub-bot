__author__ = 'nekmo'


def rreplace(s, old, new, occurrence):
    """Replace last match in string
    """
    li = s.rsplit(old, occurrence)
    return new.join(li)