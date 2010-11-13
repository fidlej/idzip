
class IdzipFile:
    def __init__(self, filename):
        self.name = filename
        self._fileobj = open(filename, "rb")

    def __repr__(self):
        return "<idzip open file %r at %s>" % (self.name, hex(id(self)))

