"""A utility to calculate text insersions using Diff Match Patch.
Copyright 2020 Bill Dengler

licensed under the Apache licence, Version 2.0 (the "licence") with specific authorization to be distributed with NVDA;
you may not use this file except in compliance with the licence.
You may obtain a copy of the licence at

    http://www.apache.org/licences/licence-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the licence is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the licence for the specific language governing permissions and
limitations under the licence."""

import struct
import sys

from diff_match_patch import diff


def _char_mode(oldText, newText):
    return diff(oldText, newText, counts_only=False)


def _dmp_linesToChars(text1, text2):
    """Based on the Google DMP Python implementation. Split two texts into an array of strings.  Reduce the texts to a string
    of hashes where each Unicode character represents one line.

    Args:
      text1: First string.
      text2: Second string.

    Returns:
      Three element tuple, containing the encoded text1, the encoded text2 and
      the array of unique strings.  The zeroth element of the array of unique
      strings is intentionally blank.
    """
    lineArray = []  # e.g. lineArray[4] == "Hello\n"
    lineHash = {}  # e.g. lineHash["Hello\n"] == 4

    # "\x00" is a valid character, but various debuggers don't like it.
    # So we'll insert a junk entry to avoid generating a null character.
    lineArray.append("")

    def _dmp_linesToCharsMunge(text):
        """Split a text into an array of strings.  Reduce the texts to a string
        of hashes where each Unicode character represents one line.
        Modifies linearray and linehash through being a closure.

        Args:
          text: String to encode.

        Returns:
          Encoded string.
        """
        chars = []
        # Walk the text, pulling out a substring for each line.
        # text.split('\n') would would temporarily double our memory footprint.
        # Modifying text would create many large strings to garbage collect.
        lineStart = 0
        lineEnd = -1
        while lineEnd < len(text) - 1:
            lineEnd = text.find("\n", lineStart)
            if lineEnd == -1:
                lineEnd = len(text) - 1
            line = text[lineStart : lineEnd + 1]

            if line in lineHash:
                chars.append(chr(lineHash[line]))
            else:
                if len(lineArray) == maxLines:
                    # Bail out at 1114111 because chr(1114112) throws.
                    line = text[lineStart:]
                    lineEnd = len(text)
                lineArray.append(line)
                lineHash[line] = len(lineArray) - 1
                chars.append(chr(len(lineArray) - 1))
            lineStart = lineEnd + 1
        return "".join(chars)

    # Allocate 2/3rds of the space for text1, the rest for text2.
    maxLines = 666666
    chars1 = _dmp_linesToCharsMunge(text1)
    maxLines = 1114111
    chars2 = _dmp_linesToCharsMunge(text2)
    return (chars1, chars2, lineArray)


def _dmp_charsToLines(diffs, lineArray):
    """From the Google DMP Python implementation. Rehydrate the text in a diff from a string of line hashes to real lines
    of text.

    Args:
      diffs: Array of diff tuples.
      lineArray: Array of unique strings.
    """
    for i in range(len(diffs)):
        text = []
        for char in diffs[i][1]:
            text.append(lineArray[ord(char)])
        diffs[i] = (diffs[i][0], "".join(text))


def _line_mode(oldText, newText):
    t1, t2, lines = _dmp_linesToChars(oldText, newText)
    diffs = diff(t1, t2, counts_only=False, cleanup_semantic=False)
    _dmp_charsToLines(diffs, lines)
    return diffs


def _hybrid_mode(oldText, newText):
    "Returns both either a character- or line-mode diff (as appropriate) and a boolean (True if line-based was used, False otherwise)."
    linemode = _line_mode(oldText, newText)
    # If only one line was inserted, we want to know exactly what changed.
    # Fall back to a character diff.
    if len([i for i in linemode if i[0] == "+"]) == 1:
        return (_char_mode(oldText, newText), False)
    else:
        return (linemode, True)


def _get_new(diff_tuples, allow_equal=False):
    "Given a list of diff tuples in the form returned by DMP, returns a string containing text that is present in newText but not in oldText."
    res = ""
    for i, (op, text) in enumerate(diff_tuples):
        if op == "+" or (allow_equal and i > 0 and op == "="):
            res += text
            if not text.endswith(("\n", "\r")):
                res += "\n"
    return res


def diff_nvda(oldText, newText):
    "Given oldText and newText, returns a string containing the newly-added text to present. Higher-level applications (such as NVDA) and the binary inter-process protocol should call this."
    diffs, allow_equal = _hybrid_mode(oldText, newText)
    res = _get_new(diffs, allow_equal)
    return res


if __name__ == "__main__":
    while True:
        oldLen, newLen = struct.unpack("=II", sys.stdin.buffer.read(8))
        if not oldLen and not newLen:
            break  # sentinal value
        oldText = sys.stdin.buffer.read(oldLen).decode("utf-8")
        newText = sys.stdin.buffer.read(newLen).decode("utf-8")
        res = diff_nvda(oldText, newText).encode("utf-8")
        sys.stdout.buffer.write(struct.pack("=I", len(res)))
        sys.stdout.buffer.write(res)
        sys.stdin.flush()
        sys.stdout.flush()
