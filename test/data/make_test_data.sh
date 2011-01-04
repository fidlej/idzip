#!/bin/sh
set -e
zcat quixote.txt.gz > quixote.txt
head -c58315 quixote.txt >one_chunk.txt
head -c116630 quixote.txt >two_chunks.txt
head -c18011 quixote.txt >small.txt
head -c134641 quixote.txt >medium.txt
rm -f quixote.txt

dictzip -k *.txt
cat medium.txt small.txt >two_members.txt
cat medium.txt.dz small.txt.dz >two_members.txt.dz
cat small.txt empty.txt medium.txt >small_empty_medium.txt
cat small.txt.dz empty.txt.dz medium.txt.dz >small_empty_medium.txt.dz
