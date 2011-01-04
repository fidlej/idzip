
class OneItemCache(object):
    """The simplest LRU cache.
    """
    def __init__(self):
        self.key = None
        self.value = None

    def get(self, key):
        if self.key == key:
            return self.value
        return None

    def put(self, key, value):
        self.key = key
        self.value = value

