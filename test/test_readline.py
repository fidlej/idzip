
from test_decompressor import create_data_readers

def test_unlimited_readline():
    for reader in create_data_readers():
        for i in xrange(100):
            reader.readline()


def test_limited_readline():
    for reader in create_data_readers():
        for i in xrange(100):
            reader.readline(20)

