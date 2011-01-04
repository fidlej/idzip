
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

    filename = "test/data/%s.dz" % basename
    output.seek(0)
    expected = open(filename, "rb")
    asserting.eq_bytes(expected.read(4), output.read(4))

    # mtime
    eq_(mtime, struct.unpack("<I", output.read(4))[0])
    expected.seek(8)

    # field header
    xlen = ord(expected.read(1)) + 256 * ord(expected.read(1))
    expected.seek(-2, os.SEEK_CUR)
    asserting.eq_bytes(expected.read(10), output.read(10))
    expected.seek(xlen - 10, os.SEEK_CUR)
    output.seek(xlen - 10, os.SEEK_CUR)

    # filename
    filename_len = len(filename) + 1
    asserting.eq_bytes(expected.read(filename_len), output.read(filename_len))

    # tail
    expected.seek(-8, os.SEEK_END)
    output.seek(-8, os.SEEK_END)
    asserting.eq_bytes(expected.read(8), output.read(8))
