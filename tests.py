import nvda_dmp
import unittest


class TestNVDADMP(unittest.TestCase):
    def test_single_char(self):
        "If there is only one line of text, nvda_dmp should perform a character diff (return exactly which characters are present in newText but not oldText)."
        self.assertEqual(nvda_dmp.diff_nvda("Cactus on ice", "Cactus on rice"), "r\n")

    def test_single_line(self):
        "If there is only one line of text, nvda_dmp should perform a character diff (return exactly which characters are present in newText but not oldText)."
        self.assertEqual(nvda_dmp.diff_nvda("Cactus cake", "Cactus cupcake"), "cup\n")

    def test_multiline_single_line_change(self):
        "In a multi-line text, if only one line of text has changed, nvda_dmp should return exactly which characters were added."
        self.assertEqual(
            nvda_dmp.diff_nvda(
                "The following is a list of cactus-themed foods\nCactus pie\nCactus tacos\nCactus cereal",
                "The following is a list of cactus-themed foods\nCactus pie\nCactus tacos\nCactus soup",
            ),
            "soup\n"
        )

    def test_multiline_multi_line_change(self):
        "In a multi-line text, if more than one line has changed, nvda_dmp should report changes at line level keeping any common text between changed sections intact."
        self.assertEqual(
            nvda_dmp.diff_nvda(
                "The following is a list of cactus-themed foods\ncactus cake\ncactus pie\ncactus cereal",
                "The following is a list of cactus-themed foods\ncactus cupcakes\ncactus pie\ncactus soup",
            ),
            "cactus cupcakes\ncactus pie\ncactus soup\n"
        )


if __name__ == "__main__":
    unittest.main()
