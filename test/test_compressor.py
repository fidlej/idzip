
from nose.tools import eq_
import struct

from cStringIO import StringIO
from idzip import compressor

def test_compress_empty():
    input = StringIO()
    output = StringIO()
    mtime = 1234

    compressor.compress(input, 0, output, "empty.txt", mtime)

    expected = open("test/data/empty.txt.dz").read()
    got = output.getvalue()

    eq_(expected[:4], got[:4])
    eq_(mtime, struct.unpack("<I", got[4:8])[0])
    eq_(expected[8:], got[8:])

