
from __future__ import with_statement

from nose.tools import eq_
import struct
import os
from cStringIO import StringIO

from idzip import compressor
import asserting

def test_reserved():
    eq_(compressor.FRESERVED, int("11100000", 2))


def test_compress_empty():
    _eq_compress("empty.txt")
    _eq_compress("empty.txt", mtime=1234)
    _eq_compress("empty.txt", mtime=1289163286)


def test_compress_chunks():
    _eq_compress("small.txt")
    _eq_compress("one_chunk.txt")
    _eq_compress("two_chunks.txt")
    _eq_compress("medium.txt")


def test_big_file():
    header = StringIO()
    in_size = compressor.MAX_MEMBER_SIZE
    compressor._prepare_header(header, in_size, None, 0)

    in_size = compressor.MAX_MEMBER_SIZE + 1
    try:
        compressor._prepare_header(header, in_size, None, 0)
    except AssertionError, expected:
        pass
    else:
        assert False, "A max member size check is missing."


def _eq_compress(basename, mtime=0):
    output = StringIO()
    with open("test/data/%s" % basename, "rb") as input:
        input.seek(0, os.SEEK_END)
        in_size = input.tell()
        input.seek(0)

        compressor.compress(input, in_size, output, basename, mtime)

    
    output.seek(0)
    expected = open("test/data/%s.dz" % basename, "rb")
    asserting.eq_bytes(expected.read(4), output.read(4))

    # mtime
    eq_(mtime, struct.unpack("<I", output.read(4))[0])
    expected.read(4)

    # XFL and OS
    asserting.eq_bytes(expected.read(2), output.read(2))

    # field header
    info_len = 10
    xlen_bytes = expected.read(2)
    asserting.eq_bytes(xlen_bytes, output.read(2))
    xlen = ord(xlen_bytes[0]) & 0xff + 256 * (ord(xlen_bytes[1]) & 0xff)
    asserting.eq_bytes(expected.read(info_len), output.read(info_len))
    expected.seek(xlen - info_len, os.SEEK_CUR)
    output.seek(xlen - info_len, os.SEEK_CUR)
    num_chunks = in_size // compressor.CHUNK_LENGTH
    if in_size % compressor.CHUNK_LENGTH:
        num_chunks += 1
    eq_(num_chunks, (xlen - info_len) // 2)

    # filename
    fname_len = len(basename) + 1
    asserting.eq_bytes(expected.read(fname_len), output.read(fname_len))

    _eq_zstream(expected, output)

    # tail
    expected.seek(-8, os.SEEK_END)
    output.seek(-8, os.SEEK_END)
    asserting.eq_bytes(expected.read(8), output.read(8))


def _eq_zstream(expected, produced):
    """Compares the zstreams.
    Their decompressed bytes are compared.
    The compressed bytes differ, because of the different
    flushing used in the Python zlib and dictzip.
    """
    import zlib
    deobj = zlib.decompressobj(-zlib.MAX_WBITS)
    expected_data = deobj.decompress(expected.read())

    deobj = zlib.decompressobj(-zlib.MAX_WBITS)
    got = deobj.decompress(produced.read())
    asserting.eq_bytes(expected_data, got)

