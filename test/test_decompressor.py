
from nose.tools import eq_

from idzip import decompressor

def test_repr():
    filename = "test/data/medium.txt.dz"
    dzfile = decompressor.IdzipFile(filename)
    eq_(dzfile.name, filename)

    file_id = hex(id(dzfile))
    eq_(repr(dzfile), "<idzip open file '%s' at %s>" % (filename, file_id))

