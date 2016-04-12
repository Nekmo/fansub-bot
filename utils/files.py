from nekbot.core.exceptions import InvalidArgument
import os

__author__ = 'nekmo'


def  remove_extension(filename):
    """Remove extension in filename
    """
    if not '.' in filename: return filename
    return '.'.join(filename.split('.')[:-1])


def set_extension(filename, ext):
    return '.'.join([filename, ext])


def split_extension(filename):
    if not '.' in filename:
        return [filename]
    return remove_extension(filename), filename.split('.')[-1]


def only_one_element(nodes, directory, type_element):
    if len(nodes) > 1:
        raise InvalidArgument('Too many %s in the directory.' % type_element, directory)
    elif not len(nodes):
        raise InvalidArgument('There are no %s in the directory.' % type_element, directory)
    return nodes[0]


def one_or_more(nodes, directory, type_element):
    if not len(nodes):
        raise InvalidArgument('There are no %s in the directory.' % type_element, directory)
    return nodes


def search_by_pattern(directory, pattern, type_element, only_one=True):
    nodes = [node for node in os.listdir(directory) if pattern.match(node)]
    return (only_one_element if only_one else one_or_more)(nodes, directory, type_element)


def create_if_not_exists(path, only_directory=False):
    if only_directory:
        path = os.path.dirname(path)
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else:
        return False