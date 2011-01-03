
from test_decompressor import create_data_readers

def test_unlimited_readline():
    for reader in create_data_readers():
        for i in xrange(10000):
            if not reader.readline():
                break


def test_limited_readline():
    for reader in create_data_readers():
        for i in xrange(10000):
            if not reader.readline(20):
                break

