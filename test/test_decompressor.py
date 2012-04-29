
from __future__ import with_statement

import os
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
    zlengths = [45, 21332, 234]
    field = struct.pack("<HHH", 1, chlen, len(zlengths))
    for zlen in zlengths:
        field += struct.pack("<H", zlen)

    dictzip_field = decompressor._parse_dictzip_field(field)
    eq_(dictzip_field["chlen"], chlen)
    eq_(dictzip_field["zlengths"], zlengths)

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


def test_begining_read():
    for reader in create_data_readers():
        for i in xrange(100):
            data = reader.read(1234)

        for i in xrange(100):
            reader.read(1)

        reader.seek(0)
        for i in xrange(2):
            reader.read(100000)


def test_end_read():
    buflen = 1234
    for reader in create_data_readers():
        filesize = reader.filesize()
        for i in xrange(100):
            reader.seek(max(0, filesize - i * buflen))
            reader.read(buflen)


def test_seek_cur():
    for reader in create_data_readers():
        for i in xrange(100):
            data = reader.read(1234)
            reader.seek(i, os.SEEK_CUR)


def test_eof():
    buflen = 1234
    for reader in create_data_readers():
        filesize = reader.filesize()
        reader.seek(filesize)
        eq_("", reader.read(1))

        if filesize > 0:
            reader.seek(filesize - 1)
            assert len(reader.read(1)) == 1


def create_data_readers():
    filenames = [
            "empty.txt",
            "medium.txt",
            "one_chunk.txt",
            "small.txt",
            "small_empty_medium.txt",
            "two_chunks.txt",
            "two_members.txt",
        ]
    readers = []
    for filename in filenames:
        expected_input = open("test/data/%s" % filename)
        input = decompressor.IdzipFile("test/data/%s.dz" % filename)
        readers.append(EqReader(expected_input, input))

    return readers


def _eq_decompress(filename):
    input = decompressor.IdzipFile("test/data/%s.dz" % filename)
    asserting.eq_files("test/data/%s" % filename, input)


class EqReader:
    def __init__(self, expected_input, input):
        self.expected_input = expected_input
        self.input = input

    def read(self, size=None):
        expected = self.expected_input.read(size)
        got = self.input.read(size)
        asserting.eq_bytes(expected, got)
        return got

    def seek(self, pos, whence=os.SEEK_SET):
        self.expected_input.seek(pos, whence)
        self.input.seek(pos, whence)
        eq_(self.expected_input.tell(), self.input.tell())

    def readline(self, size=-1):
        expected = self.expected_input.readline(size)
        got = self.input.readline(size)
        asserting.eq_bytes(expected, got)
        return got

    def filesize(self):
        self.expected_input.seek(0, os.SEEK_END)
        filesize = self.expected_input.tell()
        self.expected_input.seek(self.input.tell())
        return filesize
