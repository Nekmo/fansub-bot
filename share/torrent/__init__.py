from hashlib import md5
import os
from nekbot import settings
from utils.anime import remove_episode, remove_crc, get_episodes
from utils.files import remove_extension, create_if_not_exists
from utils.torrent import create_torrent
import tempfile

__author__ = 'nekmo'

TORRENT_PATH = os.path.join(tempfile.tempdir if tempfile.tempdir else '/tmp', 'torrent')


def get_position_if_list(elements, position=0):
    if not isinstance(elements, (tuple, list)):
        return elements
    return elements[position]


def get_torrent_file(paths):
    if len(paths) < 2:
        filename = os.path.split(paths[0])[1]
    else:
        filename = md5(''.join(paths)).hexdigest()
        filename = '%s-%s' % (get_directory_name(paths[0])[:255 - len(filename)], filename)
    torrent_file = remove_extension(os.path.join(TORRENT_PATH, filename)) + '.torrent'
    return torrent_file


def get_directory_name(path):
    directory_name = os.path.split(os.path.dirname(path))[1]
    return directory_name


def get_range_from_body(msg):
    arguments = msg.body.split(' ')
    for argument in reversed(arguments):
        if os.sep in argument:
            return argument.split(os.sep)[1]
    return ''


def get_range(msg, paths):
    range_episodes = get_range_from_body(msg)
    if range_episodes:
        return range_episodes
    paths = sorted(paths)
    first = get_position_if_list(get_episodes(paths[0]))
    last = get_position_if_list(get_episodes(paths[-1]), -1)
    if first == last:
        return first
    if first is None and last is not None:
        first = 1
    if last is None:
        return None
    return '%i-%i' % (first, last)


def get_packs_name(msg, directory_name, pack_range):
    if getattr(msg, 'is_share', False) and hasattr(settings, 'PACK_SHARE_DIRECTORY') and pack_range is not None:
        pattern = settings.PACK_SHARE_DIRECTORY
    else:
        pattern = settings.PACK_DIRECTORY
    return pattern.format(**locals())


def torrent(msg, paths):
    if not os.path.exists(TORRENT_PATH):
        os.makedirs(TORRENT_PATH)
    directory_name = get_packs_name(msg, get_directory_name(paths[0]), get_range(msg, paths))
    torrent_file = get_torrent_file(paths)
    create_torrent(paths, torrent_file, settings.TORRENT_URL_INFO, directory_name)
    if getattr(settings, 'TORRENT_FILE_TO_PATH'):
        create_if_not_exists(settings.TORRENT_FILE_TO_PATH)
        dest = os.path.join(settings.TORRENT_FILE_TO_PATH, os.path.split(torrent_file)[1])
        if not os.path.exists(dest):
            os.symlink(torrent_file, dest)
    if getattr(settings, 'TORRENT_DATA_TO_PATH'):
        if len(paths) > 1:
            dest = os.path.join(settings.TORRENT_DATA_TO_PATH, directory_name)
            create_if_not_exists(dest)
            for path in paths:
                file_dest = os.path.join(dest, os.path.split(path)[1])
                if os.path.exists(file_dest):
                    continue
                os.symlink(path, file_dest)
        else:
            create_if_not_exists(settings.TORRENT_DATA_TO_PATH)
            os.symlink(torrent_file, os.path.join(settings.TORRENT_DATA_TO_PATH, os.path.split(paths[0])[1]))
