
from __future__ import with_statement
from nose.tools import eq_
import struct

from cStringIO import StringIO
from idzip import compressor

def test_compress_empty():
    _eq_data("empty.txt")
    _eq_data("empty.txt", mtime=1234)
    _eq_data("empty.txt", mtime=1289163286)


def test_compress_one_chunk():
    #TODO: enable
    #_eq_data("one_chunk.txt")
    pass


def _eq_data(basename, mtime=0):
    input = StringIO()
    output = StringIO()

    compressor.compress(input, 0, output, basename, mtime)

    with open("test/data/%s.dz" % basename) as dzfile:
        expected = dzfile.read()
    got = output.getvalue()

    eq_(expected[:4], got[:4])
    eq_(mtime, struct.unpack("<I", got[4:8])[0])
    eq_(expected[8:], got[8:])

