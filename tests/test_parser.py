import unittest

from browser.parser import HTMLParser, print_tree


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
        print(meta)
        content = meta.attributes["content"]
        self.assertEqual(content, "dark light")

    def test_nested_paragraphs(self):
        tree = HTMLParser("<p>hello<p>world</p>").parse()
        body = find_tag(tree, "body")
        self.assertEqual(len(body.children), 2)


if __name__ == "__main__":
    unittest.main()
