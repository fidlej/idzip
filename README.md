The **idzip** file format allows seeking in gzip files.

Features:
  * efficient seeking in the compressed data
  * no 4GB limit
  * compatible with gzip

Provided interface:
  * `idzip`, `gunzip`, `zcat` command line utilities
  * Python function `idzip.open(filename)` for transparent reading

Gzip allows to store extra fields in the gzip header. Idzip stores offsets for the efficient seeking there.


### Acknowledgement ###
The [file format](http://manpages.ubuntu.com/manpages/precise/man1/dictzip.1.html) was designed by Rik Faith for [dictzip](https://sourceforge.net/projects/dict/). Idzip just uses multiple [gzip members](http://tools.ietf.org/html/rfc1952#page-5) to have no file size limit.<br />
Idzip means Improved Dictzip.
