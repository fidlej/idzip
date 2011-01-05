
def open(filename):
    from idzip.decompressor import IdzipFile
    try:
        return IdzipFile(filename)
    except IOError, e:
        import logging
        import gzip
        logging.info("Using gzip fallback: %r", e)
        return gzip.open(filename, "rb")

