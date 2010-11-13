#!/usr/bin/env python
"""Usage: compress.py FILE
Compresses the given file.
"""

import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent_dir)
from idzip import compressor

SUFFIX = ".dz"

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) == 0:
        print >>sys.stderr, __doc__
        sys.exit(1)

    for filename in args:
        input = open(filename, "rb")
        inputinfo = os.fstat(input.fileno())
        basename = os.path.basename(filename)

        output = open(filename + SUFFIX, "wb")
        compressor.compress(input, inputinfo.st_size, output,
                basename, int(inputinfo.st_mtime))

        output.close()
        input.close()


if __name__ == "__main__":
    main()

