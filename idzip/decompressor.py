
import struct
import zlib
from cStringIO import StringIO

from idzip import compressor

# The gzip tail contains 4 bytes for CRC and 4 bytes for of the file size.
GZIP_TAIL_LEN = 8


class IdzipFile:
    def __init__(self, filename):
        self.name = filename
        self._fileobj = open(filename, "rb")
        # The current position in the decompressed data.
        self._pos = 0
        self._chlen = None
        self._chunks = []

        self._read_member_header()

    def _read_member_header(self):
        """Fills self._chlen and self._chunks
        by the read header data.
        """
        header = _read_gzip_header(self._fileobj)
        offset = self._fileobj.tell()
        if "RA" not in header["extra_field"]:
            raise IOError("Not an idzip file: %r" % self.name)

        dictzip_field = _parse_dictzip_field(header["extra_field"]["RA"])
        if self._chlen is None:
            self._chlen = dictzip_field["chlen"]
        elif self._chlen != dictzip_field["chlen"]:
            raise IOError(
                    "Members with different chunk length are not supported.")

        self._chunks = []
        for comp_len in dictzip_field["comp_lengths"]:
            self._chunks.append((offset, comp_len))
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
        """Reads the specified chunk or throws EOFError.
        """
        while chunk_index >= len(self._chunks):
            self._reach_member_end()
            _read_member_header()

        #TODO: implement

    def _reach_member_end(self):
        """Seeks the _fileobj at the end of the last known member.
        """
        offset, comp_len = self._chunks[-1]
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


def _read_gzip_header(input):
    """Returns a parsed gzip header.
    The position of the input is advanced beyond the header.
    EOFError is throws if there is not enough of data for the header.
    """
    header = {
            "extra_field": {}
            }

    magic, flags, mtime = struct.unpack("<3sbIxx", _read_exactly(input, 10))
    if magic != compressor.GZIP_DEFLATE_ID:
        raise IOError("Not a gzip-deflate file.")

    if compressor.FEXTRA & flags:
        xlen = _read16(input)
        extra_field = input.read(xlen)
        header["extra_field"] = _split_subfields(extra_field)

    if compressor.FNAME & flags:
        _skip_cstring(input)

    if compressor.FCOMMENT & flags:
        _skip_cstring(input)

    if compressor.FHCRC & flags:
        # Skips header CRC
        input.read(2)

    return header


def _read_exactly(input, size):
    data = input.read(size)
    if len(data) != size:
        raise EOFError, "Reached EOF"
    return data


def _read16(input):
    """Reads next two bytes as an integer.
    """
    return struct.unpack("<H", _read_exactly(input, 2))[0]


def _split_subfields(extra_field):
    """Returns a dict with {sub_id: subfield_data} entries.
    The extra field contains a variable number of bytes
    for each subfields:
    +---+---+---+---+===============================+
    |SUB_ID |  LEN  | LEN bytes of subfield data ...|
    +---+---+---+---+===============================+
    """
    input = StringIO(extra_field)
    sub_fields = {}
    while True:
        sub_id = input.read(2)
        if not sub_id:
            return sub_fields

        data_len = _read16(input)
        sub_fields[sub_id] = input.read(data_len)

def _skip_cstring(input):
    """Reads and discards a zero-terminated string.
    """
    while True:
        c = input.read(1)
        if not c or c == "\0":
            return

def _parse_dictzip_field(subfield):
    """Returns a dict with:
        chlen ... length of each uncompressed chunk,
        comp_lengths ... lengths of compressed chunks.

    The dictzip subfield consists of:
    +---+---+---+---+---+---+==============================================+
    | VER=1 | CHLEN | CHCNT | CHCNT 2-byte lengths of compressed chunks ...|
    +---+---+---+---+---+---+==============================================+
    """
    input = StringIO(subfield)
    ver, chlen, chunk_count = struct.unpack("<HHH", input.read(6))
    if ver != 1:
        raise IOError("Unsupported dictzip version: %s" % ver)

    comp_lengths = []
    for i in xrange(chunk_count):
        comp_lengths.append(_read16(input))

    return dict(chlen=chlen, comp_lengths=comp_lengths)

