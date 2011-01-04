
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


def test_compress_multiple_members():
    mtime = 1234
    first_size = _inputsize(open("test/data/medium.txt", "rb"))
    second_size = _inputsize(open("test/data/small.txt", "rb"))
    assert first_size >= second_size

    orig = compressor.MAX_MEMBER_SIZE
    try:
        compressor.MAX_MEMBER_SIZE = first_size
        produced = _mem_compress("two_members.txt", mtime)
    finally:
        compressor.MAX_MEMBER_SIZE = orig

    expected = open("test/data/two_members.txt.dz", "rb")
    _eq_zformat(expected, produced, mtime, expected_basename="two_members.txt",
            in_size=first_size)
    _eq_zformat(expected, produced, mtime=0, expected_basename=None,
            in_size=second_size)


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
    output = _mem_compress(basename, mtime)
    expected = open("test/data/%s.dz" % basename, "rb")
    _eq_zformat(expected, output, mtime, expected_basename=basename)


def _mem_compress(basename, mtime=0):
    output = StringIO()
    with open("test/data/%s" % basename, "rb") as input:
        in_size = _inputsize(input)
        compressor.compress(input, in_size, output, basename, mtime)

    output.seek(0)
    return output


def _inputsize(input):
    input.seek(0, os.SEEK_END)
    in_size = input.tell()
    input.seek(0)
    return in_size


def _eq_zformat(expected, output, mtime=0, expected_basename=None, in_size=None):
    """Compares the file formats of data in the given streams.
    """
    if in_size is None:
        expected.seek(-4, os.SEEK_END)
        in_size = struct.unpack("<I", expected.read(4))[0]
        expected.seek(0)

    # ID1,ID2,CM
    asserting.eq_bytes(expected.read(3), output.read(3))

    # flags
    flags = ord(expected.read(1)) & 0xff
    if expected_basename is None:
        flags = flags - compressor.FNAME
    eq_(flags, ord(output.read(1)) & 0xff)

    # mtime
    eq_(mtime, struct.unpack("<I", output.read(4))[0])
    expected.read(4)

    # XFL and OS
    asserting.eq_bytes(expected.read(2), output.read(2))

    # FEXTRA header
    info_len = 10
    xlen_bytes = expected.read(2)
    asserting.eq_bytes(xlen_bytes, output.read(2))

    xlen = ord(xlen_bytes[0]) & 0xff + 256 * (ord(xlen_bytes[1]) & 0xff)
    num_chunks = in_size // compressor.CHUNK_LENGTH
    if in_size % compressor.CHUNK_LENGTH:
        num_chunks += 1
    eq_(num_chunks, (xlen - info_len) // 2)

    asserting.eq_bytes(expected.read(info_len), output.read(info_len))
    expected.seek(xlen - info_len, os.SEEK_CUR)
    output.seek(xlen - info_len, os.SEEK_CUR)

    # FNAME
    fname = _read_cstring(expected)
    if expected_basename is not None:
        eq_(expected_basename, _read_cstring(output))

    # zstream
    _eq_zstream(expected, output)

    # tail
    asserting.eq_bytes(expected.read(8), output.read(8))


def _read_cstring(input):
    text = ""
    while True:
        c = input.read(1)
        if c == "\0":
            return text

        text += c


def _eq_zstream(expected, produced):
    """Compares the zstreams.
    Their decompressed bytes are compared.
    The compressed bytes differ, because of the different
    flushing used in the Python zlib and dictzip.
    """
    import zlib
    deobj = zlib.decompressobj(-zlib.MAX_WBITS)
    expected_data = deobj.decompress(expected.read())
    expected.seek(-len(deobj.unused_data), os.SEEK_CUR)

    deobj = zlib.decompressobj(-zlib.MAX_WBITS)
    got = deobj.decompress(produced.read())
    produced.seek(-len(deobj.unused_data), os.SEEK_CUR)
    asserting.eq_bytes(expected_data, got)

