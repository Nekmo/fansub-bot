import os
from create_video import get_video_name, search_video_paths, create_video
from fields import DirMultiplesRootsWithRange
from nekbot import settings
from nekbot.core.commands import command
from nekbot.core.commands.control import control
from utils.anime import set_crc

__author__ = 'nekmo'


def get_final_path(directory, final_name):
    final_directory = os.path.join(directory, 'mux')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    final_path = os.path.join(final_directory, final_name)
    return final_path


@command('premux', DirMultiplesRootsWithRange(settings.OWN_WORK_DIRECTORY, settings.FOREIGN_WORK_DIRECTORY))
@control('admin')
def premux(msg, directories):
    for directory in directories:
        path_with_crc = premux_video(msg, directory)
        msg.reply('Created new file in %s' % path_with_crc, notice=True)


def premux_video(msg, directory):
    chapters_path, fonts_dir, subtitles_path, video_extension, video_name, video_path = search_video_paths(directory)
    video_name = get_video_name(directory, video_extension, video_name, video_path)
    final_path = get_final_path(directory, video_name)
    msg.reply('Please, wait while video is generated. Be patient! Look lolis!!', notice=True)
    create_video(msg, video_path, final_path, subtitles_path, fonts_dir, chapters_path)
    path_with_crc = set_crc(final_path)
    return path_with_crc