
def open(filename):
    from idzip.decompressor import IdzipFile
    return IdzipFile(filename)

