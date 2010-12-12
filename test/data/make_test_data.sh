#!/bin/sh
set -e
dictzip -k *.txt
cat small.txt medium.txt >two_members.txt
cat small.txt.dz medium.txt.dz >two_members.txt.dz
