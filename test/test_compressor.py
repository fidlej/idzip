
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
    eq_(mtime, struct.unpack("<I", output.read(4))[0])
    expected.seek(8)
    asserting.eq_files(expected, output)

