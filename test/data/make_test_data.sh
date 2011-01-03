#!/bin/sh
set -e
dictzip -k *.txt
cat small.txt medium.txt >two_members.txt
cat small.txt.dz medium.txt.dz >two_members.txt.dz
cat small.txt empty.txt medium.txt >small_empty_medium.txt
cat small.txt.dz empty.txt.dz medium.txt.dz >small_empty_medium.txt.dz
