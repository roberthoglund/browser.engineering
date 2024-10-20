import unittest

from browser.parser import HTMLParser


def find_tag(tree, tag):
    if tree.tag == tag:
        return tree
    for child in tree.children:
        result = find_tag(child, tag)
        if result:
            return result
    return None


class MyTestCase(unittest.TestCase):
    def test_quoted_attributes(self):
        tree = HTMLParser('<meta content="dark light"/>').parse()
        meta = find_tag(tree, "meta")
        content = meta.attributes["content"]
        self.assertEqual(content, "dark light")


if __name__ == "__main__":
    unittest.main()
