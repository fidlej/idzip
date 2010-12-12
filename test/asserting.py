
from nose.tools import eq_

def eq_files(expected_input, got_input):
    if isinstance(expected_input, basestring):
        expected_input = open(expected_input, "rb")
    expected = expected_input.read()
    expected_input.close()
    got = got_input.read()
    got_input.close()

    eq_bytes(expected, got)


def eq_bytes(a, b):
    i = 0
    for i, (ac, bc) in enumerate(zip(a, b)):
        if ac != bc:
            break

    context_size = 10
    assert a == b, "at %s: %r != %r" % (i,
            a[i:i+context_size], b[i:i+context_size])

