# NVDA_dmp
A proxy to allow NVDA to use [diff-match-patch](https://github.com/JoshData/diff_match_patch-python) without linking for [licensing reasons](https://www.apache.org/licenses/GPL-compatibility.html).

Copyright 2020 Bill Dengler, licensed under [apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) with explicit authorization to be distrinbuted with the [NVDA screen reader](https://nvaccess.org).

## Protocol
NVDA_dmp expects to receive old and new text on stdin, and writes on stdout text that was inserted (i.e. new changes that NVDA should speak). The protocol is as follows:

* Input: two 32-bit ints (in machine byte order) containing the lengths (in bytes) of the old and new texts respectively. Immediately following, write the old text, then new (encoded in utf-8).
* Output: a 32-bit int containing the length of the output, then any text which was inserted (i.e. present in new but not in old).