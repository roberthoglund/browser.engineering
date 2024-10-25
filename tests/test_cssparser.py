import unittest

from browser.css_parser import CSSParser


class MyTestCase(unittest.TestCase):
    def test_something(self):
        props = CSSParser("background-color: lightblue").body()
        self.assertTrue("background-color" in props)
        self.assertEqual(props["background-color"], "lightblue")


if __name__ == "__main__":
    unittest.main()
