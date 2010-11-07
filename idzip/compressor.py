
import zlib
import struct
from cStringIO import StringIO

MAX_MEMBER_SIZE = 1800 * 1024 * 1024  # 1800MB
CHUNK_LENGTH = 58315  # chunk length used by dictzip

# slow compression is OK
COMPRESSION_LEVEL = zlib.Z_BEST_COMPRESSION


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
    header_io = StringIO()
    _prepare_header(header_io, in_size, basename, mtime)
    output.write(header_io.getvalue())

    #TODO: Form the chunks by flushing the compressor.
    #TODO: Write the known chunk lengths to the header.
    #TODO: Raise an error if the in_size is too big.

    crcval = zlib.crc32("")
    compobj = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED,
            -zlib.MAX_WBITS)

    need = in_size
    while need > 0:
        read_size = min(need, CHUNK_LENGTH)
        data = input.read(read_size)
        if len(data) != read_size:
            raise IOError("Need %s bytes, got %s" % (read_size, len(data)))

        need -= len(data)
        crcval = zlib.crc32(data, crcval)
        output.write(compobj.compress(data))

    output.write(compobj.flush())
    _write32(output, crcval)
    _write32(output, in_size)


def _prepare_header(output, in_size, basename, mtime):
    """Returns a prepared gzip header StringIO.
    The gzip header is defined in RFC 1952.
    """
    output.write("\x1f\x8b\x08")  # Gzip-deflate identification
    if basename:
        output.write("\x08")  # FNAME flag

    # The mtime will be undefined if it does not fit.
    if mtime > 0xffffffffL:
        mtime = 0
    _write32(output, mtime)

    deflate_flags = "\0"
    if COMPRESSION_LEVEL == zlib.Z_BEST_COMPRESSION:
        deflate_flags = "\x02"  # slowest compression algorithm
    output.write(deflate_flags)
    output.write('\xff')  # OS unknown

    _write_extra_fields(output, in_size)
    if basename:
        output.write(basename + '\0')  # original basename


    #TODO: add also the extra field with chunks

def _write_extra_fields(output, in_size):
    """Writes the dictzip extra field.
    It will be initiated with zeros in chunk lengths.
    See man dictzip.
    """
    num_chunks = in_size // CHUNK_LENGTH
    if in_size % CHUNK_LENGTH != 0:
        num_chunks += 1

    field_length = 3*2 + 2 * num_chunks
    extra_length = 2*2 + field_length
    assert extra_length <= 0xffff
    _write16(output, extra_length)  # XLEN

    # Dictzip extra field (Random Access)
    output.write("RA")
    _write16(output, field_length)
    _write16(output, 1)  # version
    _write16(output, CHUNK_LENGTH)
    _write16(output, num_chunks)
    output.write("\0\0" * num_chunks)


def _write16(output, value):
    """Writes only the lowest 2 bytes from the given number.
    """
    output.write(struct.pack("<H", value & 0xffff))

def _write32(output, value):
    """Writes only the lowest 4 bytes from the given number.
    """
    output.write(struct.pack("<I", value & 0xffffffffL))

