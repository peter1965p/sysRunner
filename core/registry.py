class NodeRegistry:
    def __init__(self):
        self.nodes = {}

    def register(self, name, node):
        self.nodes[name] = node

    def get(self, name):
        return self.nodes.get(name)
