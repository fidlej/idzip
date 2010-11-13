
import zlib

# The gzip tail contains 4 bytes for CRC and 4 bytes for of the file size.
GZIP_TAIL_LEN = 8


class IdzipFile:
    def __init__(self, filename):
        self.name = filename
        self._fileobj = open(filename, "rb")
        # Position in the decompressed data.
        self._pos = 0
        self._chlen = None

        self._read_member_header()

    def _read_member_header(self):
        header = _read_gzip_header(self._fileobj)
        offset = self._fileobj.tell()
        if "RA" not in header["extra_field"]:
            raise IOError("Not an idzip file: %r" % self.name)

        dictzip_field = _parse_dictzip_field(header["extra_field"]["RA"])
        if self._chlen is None:
            self._chlen = dictzip_field["chlen"]
        elif self._chlen != dictzip_field["chlen"]
            raise IOError(
                    "Members with different chunk length are not supported.")

        self._chunks = []
        for comp_len in dictzip_field["chunks"]:
            self.chunks.append((offset, comp_len))
            offset += comp_len

    def read(self, size=-1):
        chunk_index = self._pos // self._chlen
        #TODO: consider using StringIO for the result buffer
        result = ""
        need = size
        try:
            while need > 0:
                chunk_data = self._readchunk(chunk_index)
                result += chunk_data[:need]
                need = size - len(result)
                chunk_index += 1

        except EOFError:
            pass

        self._pos += len(result)
        return result

    def _readchunk(self, chunk_index):
        while chunk_index >= len(self.chunks):
            self._reach_member_end()
            _read_member_header()

    def _reach_member_end(self):
        """Seeks the _fileobj at the end of the last known member.
        """
        offset, comp_len = self.chunks[-1]
        self._fileobj.seek(offset + comp_len)
        # The zlib stream could end with an empty block.
        deobj = zlib.decompressobj(-zlib.MAX_WBITS)
        extra = ""
        while deobj.unused_data == "" and not extra:
            extra += deobj.decompress(self.fileobj.read(3))

        extra += deobj.flush()
        if extra != "":
            raise IOError("Found extra compressed data after chunks.")

        self._fileobj.seek(GZIP_TAIL_LEN - len(deobj.unused_data))

    def tell(self):
        return self._pos

    def __repr__(self):
        return "<idzip open file %r at %s>" % (self.name, hex(id(self)))


def _read_gzip_header(fileobj):
    """Returns a parsed gzip header.
    The position of the fileobj is advanced beyond the header.
    EOFError is throws if there is not enough of data for the header.
    """
    #TODO: implement

