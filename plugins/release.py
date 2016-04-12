# coding=utf-8
import re
import os

from create_video import search_video_paths, get_video_name, create_video
from fields import DirMultiplesRootsWithRange, NodeMultiplesRoots
from nekbot.utils.modules import get_module

try:
    from merge import MkvMerge
except:
    from mkv.merge import MkvMerge
from nekbot import settings
from nekbot.core.commands import command
from nekbot.core.commands.control import control
from utils.anime import remove_crc, remove_episode, get_short_name, remove_short_name_tag, set_crc
from utils.files import remove_extension

__author__ = 'nekmo'

def process_dir_video_name(name):
    for processor in settings.DIR_VIDEO_NAME_PROCESSORS:
        name = processor(name)
    return name


def get_final_path(filename):
    short_name = (get_short_name(filename)).lower()
    if short_name == settings.FANSUB_SHORT_NAME.lower():
        path = settings.OWN_RELEASES
    else:
        path = settings.FOREIGN_RELEASES
    path = os.path.join(path, process_dir_video_name(remove_crc(remove_extension(remove_episode(filename)))))
    path = os.path.join(path, filename)
    return path


def get_final_name(filename, own_work=True):
    if own_work:
        filename = remove_short_name_tag(filename)
        filename = '[%s]%s' % (settings.FANSUB_SHORT_NAME, filename)
    for pattern in settings.TAGS_TO_REMOVE:
        filename = re.sub(pattern, '', filename)
    return filename


def execute_method(msg, paths, method, action):
    msg.reply('Uploading to %s' % method, notice=True)
    try:
        module = get_module('share.{share_method}.{share_method}'.format(share_method=method))
        response = module(msg, paths)
    except Exception as e:
        msg.reply('Error %s to %s: %s' % (action, method, e), notice=True)
    else:
        if response is not None:
            msg.reply(u'%s response: %s' % (method, response))


def share_video(msg, paths):
    for share_method in settings.SHARE_VIDEO:
        execute_method(msg, paths, share_method, 'uploading')


def publish_video(msg, paths):
    for publish_method in settings.SHARE_VIDEO:
        execute_method(msg, paths, publish_method, 'publishing')


@command('release', DirMultiplesRootsWithRange(settings.OWN_WORK_DIRECTORY, settings.FOREIGN_WORK_DIRECTORY))
@control('admin')
def release(msg, directories):
    results = []
    for directory in directories:
        results.append(release_video(msg, directory))
    share_video(msg, results)
    # publish_video(msg, results)


@command('share', NodeMultiplesRoots(settings.OWN_RELEASES, settings.FOREIGN_RELEASES))
def share(msg, node):
    if os.path.isdir(node):
        nodes = [os.path.join(node, element) for element in os.listdir(node)]
    else:
        nodes = [node]
    msg.is_share = True
    share_video(msg, nodes)


def release_video(msg, directory):
    chapters_path, fonts_dir, subtitle_path, video_extension, video_name, video_path = search_video_paths(directory)
    video_name = get_video_name(directory, video_extension, video_name, video_path)
    final_name = get_final_name(video_name, True if directory.startswith(settings.OWN_WORK_DIRECTORY) else False)
    final_path = get_final_path(final_name)
    msg.reply('Please, wait while video is generated. Be patient! Look lolis!!', notice=True)
    create_video(msg, video_path, final_path, subtitle_path, fonts_dir, chapters_path)
    path_with_crc = set_crc(final_path)
    msg.reply('Created new file in %s' % path_with_crc, notice=True)
    return path_with_crc


