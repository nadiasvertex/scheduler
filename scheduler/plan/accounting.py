__author__ = 'Christopher Nelson'


class JobEntry:
    def __init__(self, name, schedule, tags=(), nodes=()):
        self.name = name
        self.schedule = schedule
        self.tags = tags

        self.running = False
        self.nodes = list(nodes)

    def add_node(self, node):
        self.nodes.append(node)

    def drop_node(self, node):
        self.nodes.remove(node)

