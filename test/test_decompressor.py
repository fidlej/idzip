
from __future__ import with_statement

import struct
from nose.tools import eq_

from idzip import decompressor
import asserting

def test_repr():
    filename = "test/data/medium.txt.dz"
    dzfile = decompressor.IdzipFile(filename)
    eq_(dzfile.name, filename)

    file_id = hex(id(dzfile))
    eq_(repr(dzfile), "<idzip open file '%s' at %s>" % (filename, file_id))


def test_parse_dictzip_field():
    chlen = 1234
    comp_lengths = [45, 21332, 234]
    field = struct.pack("<HHH", 1, chlen, len(comp_lengths))
    for comp_len in comp_lengths:
        field += struct.pack("<H", comp_len)

    dictzip_field = decompressor._parse_dictzip_field(field)
    eq_(dictzip_field["chlen"], chlen)
    eq_(dictzip_field["comp_lengths"], comp_lengths)

    field = struct.pack("<HHHH", 2, chlen, 1, 1234)
    try:
        decompressor._parse_dictzip_field(field)
        assert False
    except IOError, expected:
        pass


def test_decompress():
    _eq_decompress("small.txt")
    _eq_decompress("one_chunk.txt")
    _eq_decompress("two_chunks.txt")
    _eq_decompress("medium.txt")
    _eq_decompress("two_members.txt")


def test_decompress_empty():
    _eq_decompress("empty.txt")
    _eq_decompress("small_empty_medium.txt")


def _eq_decompress(filename):
    input = decompressor.IdzipFile("test/data/%s.dz" % filename)
    asserting.eq_files("test/data/%s" % filename, input)

