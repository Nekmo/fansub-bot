import os
import re
from nekbot.core.exceptions import InvalidArgument
from nekbot.core.types.filesystem import MultiplesRootsMix, Dir, Node

__author__ = 'nekmo'


class NodeMultiplesRoots(MultiplesRootsMix, Node):
    pass


class DirMultiplesRoots(MultiplesRootsMix, Dir):
    pass


class DirMultiplesRootsWithRange(MultiplesRootsMix, Dir):
    def default_call(self, node):
        return [super(DirMultiplesRootsWithRange, self).__call__(node)]

    def __call__(self, node):
        if not os.sep in node:
            return self.default_call(node)
        dirname, node_name = os.path.split(node)
        nodes_range = re.match('^(\d+)\-(\d+)$', node_name)
        if not nodes_range:
            return self.default_call(node)
        start, end = map(int, [nodes_range.group(1), nodes_range.group(2)])
        if not end > start:
            raise InvalidArgument('Start range should be less than end range.', node)
        nodes = []
        for i in range(start, end + 1):
            node_now = os.path.join(dirname, ('%%0%ii' % len(nodes_range.group(1))) % i)
            nodes.append(super(DirMultiplesRootsWithRange, self).__call__(node_now))
        return nodes
