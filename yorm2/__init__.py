__version__ = "0.1.0"


from functools import wraps


def sync(path, *, attrs=None):
    def decorated_class(cls):
        return cls

    return decorated_class


class Mapper:
    def __init__(self, synchronized_object):
        self._object = synchronized_object

    @property
    def attrs(self):
        return {}

    @property
    def path(self):
        return "tmp/42.yml"

    @property
    def data(self):
        return {}


def get_mapper(synchronized_object):
    return Mapper(synchronized_object)
