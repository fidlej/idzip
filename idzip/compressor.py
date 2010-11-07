
import struct
from cStringIO import StringIO

MAX_MEMBER_SIZE = 1800 * 1024 * 1024  # 1800MB
CHUNK_LENGTH = 58315  # chunk length used by dictzip

# slow compression is OK
COMPRESSION_LEVEL = 9


def compress(input, in_size, output, basename=None, mtime=0):
    while True:
        member_size = min(in_size, MAX_MEMBER_SIZE)
        _compress_member(input, member_size, output, basename, mtime)
        # Only the first member will carry the basename and mtime.
        basename = None
        mtime = 0

        in_size -= member_size
        if in_size == 0:
            return


def _compress_member(input, in_size, output, basename, mtime):
    header_io = _prepare_header(in_size, basename, mtime)
    output.write(header_io.getvalue())

    #TODO: write the compressed data
    #TODO: write the crc and file size


def _prepare_header(in_size, basename, mtime):
    """Returns a prepared gzip header StringIO.
    The gzip header is defined in RFC 1952.
    """
    header = StringIO()
    header.write("\x1f\x8b\x08")  # Gzip-deflate identification
    if basename:
        header.write("\x08")  # FNAME flag

    # The mtime will be undefined if it does not fit.
    if mtime > 0xffffffffL:
        mtime = 0
    _write32(header, mtime)

    deflate_flags = "\0"
    if COMPRESSION_LEVEL == 9:
        deflate_flags = "\x02"  # slowest compression algorithm
    header.write(deflate_flags)
    header.write('\xff')  # OS unknown
    if basename:
        header.write(basename + '\0')  # original basename

    #TODO: add also the extra field with chunks
    return header


def _write32(output, value):
    """Writes only the lowest 4 bytes from the given number.
    """
    output.write(struct.pack("<I", value & 0xffffffffL))

