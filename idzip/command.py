#!/usr/bin/env python
"""Usage: %prog [OPTION]... FILE...
Compresses the given files.
"""

import os
import sys
import optparse
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent_dir)
import idzip
from idzip import compressor

SUFFIX = ".dz"

def _parse_args():
    parser = optparse.OptionParser(__doc__)
    parser.add_option("-d", "--decompress", action="store_true",
            help="decompress the file")
    parser.add_option("-v", "--verbose", action="count",
            help="increase verbosity")
    parser.set_defaults(verbose=0)

    #TODO: use argv[0] to detect idzcat or idunzip
    #TODO: And also modify the help for them.
    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error("An input file is required.")

    return options, args


def _compress(filename, options):
    input = open(filename, "rb")
    inputinfo = os.fstat(input.fileno())
    basename = os.path.basename(filename)

    target = filename + SUFFIX
    logging.info("compressing %r to %r", filename, target)
    output = open(target, "wb")
    compressor.compress(input, inputinfo.st_size, output,
            basename, int(inputinfo.st_mtime))

    output.close()
    input.close()


def _decompress(filename, options):
    input = idzip.open(filename)

    target = _get_decompression_target(filename)
    logging.info("uncompressing %r to %r", filename, target)
    output = open(target, "wb")
    while True:
        data = input.read(1024)
        if not data:
            break

        output.write(data)

    output.close()
    input.close()


def _get_decompression_target(filename):
    head, tail = os.path.split(filename)
    parts = tail.rsplit(".", 1)
    if len(parts) != 2 or not parts[0]:
        return filename + ".undz"

    return os.path.join(head, parts[0])


def main():
    options, args = _parse_args()
    logging.basicConfig(level=logging.WARNING - 10*options.verbose)

    action = _compress
    if options.decompress:
        action = _decompress

    for filename in args:
        action(filename, options)


if __name__ == "__main__":
    main()

