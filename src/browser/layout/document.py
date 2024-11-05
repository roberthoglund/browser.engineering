from browser.layout import H_STEP, V_STEP
from browser.layout.block import BlockLayout


class DocumentLayout:
    def __init__(self, node, total_width: int):
        self.node = node
        self.total_width = total_width
        self.parent = None
        self.children = []

        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = self.total_width - 2 * H_STEP
        self.x = H_STEP
        self.y = V_STEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []
