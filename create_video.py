# coding=utf-8
import os
import re
from enzyme import MKV
import logging
from plugins.fansub_conf import get_data, get_config_path

try:
    from merge import MkvMerge
except ImportError:
    from mkv.merge import MkvMerge
try:
    from source import MkvSource
except ImportError:
    from mkv.source import MkvSource
from nekbot import settings
from nekbot.core.exceptions import PrintableException
from utils.files import search_by_pattern, set_extension, split_extension

__author__ = 'nekmo'


logging.getLogger("enzyme.parsers.ebml.core").setLevel(logging.WARNING)
logging.getLogger("enzyme.mkv").setLevel(logging.WARNING)


VIDEO_PATTERN = re.compile(".+\.(mkv)$")
SUBTITLE_PATTERN = re.compile(".+\.(ass|ssa)$")
CHAPTERS_PATTERN = re.compile(".+\.(xml)$")
FONTS_PATTERN = settings.FONTS_DIR_PATTERN


def process_video_name(name):
    for processor in settings.VIDEO_NAME_PROCESSORS:
        name = processor(name)
    return name


def search_video_paths(directory):
    video_name = search_by_pattern(directory, VIDEO_PATTERN, 'videos')
    video_extension = video_name.split('.')[-1]
    video_path = os.path.join(directory, video_name)
    subtitles_path = map(lambda x: os.path.join(directory, x),
                         search_by_pattern(directory, SUBTITLE_PATTERN, 'subtitles', False))
    try:
        chapters_path = os.path.join(directory, search_by_pattern(directory, CHAPTERS_PATTERN, 'chapters'))
    except:
        chapters_path = None
    fonts_dir = os.path.join(directory, search_by_pattern(directory, FONTS_PATTERN, 'fonts dirs'))
    return chapters_path, fonts_dir, subtitles_path, video_extension, video_name, video_path


def get_video_name(directory, video_extension, video_name, video_path):
    # Capítulo de la serie
    chapter = directory.split(os.sep)[-1]
    directory_tvshow = os.path.dirname(directory)
    # Un archivo con el nombre que ponerle a la serie
    name_file_path = os.path.join(os.path.dirname(directory), 'name.txt')
    if os.path.exists(name_file_path):
        video_name = open(name_file_path, 'r').read().replace('\n', '')
        video_name = serialize_video_name(video_name, chapter, video_extension)
    elif get_data(get_config_path(directory_tvshow)).get('name'):
        video_name = get_data(get_config_path(directory_tvshow))['name']
        video_name = serialize_video_name(video_name, chapter, video_extension)
    else:
        video_title = get_video_title(video_path)  # Título que se encuentra dentro del vídeo
        if video_title:
            video_name = set_extension(video_title, video_extension)
    video_name = process_video_name(video_name)
    if get_data(get_config_path(directory_tvshow)).get('tag'):
        video_name, extension = split_extension(video_name)
        video_name = '%s[%s]' % (video_name, get_data(get_config_path(directory_tvshow))['tag'])
        video_name = '.'.join([video_name, extension])
    return video_name


def serialize_video_name(video_name, chapter, video_extension):
    video_name = video_name.format(chapter=chapter)
    video_name = set_extension(video_name, video_extension)
    return video_name


def create_video(msg, video, dest, subtitles, fonts_dir, chapters=None):
    mkv = MKV(open(video, 'rb'))
    if len(mkv.video_tracks) > 1:
        msg.send_warning('More than one attached video.')
    # Detect audios in japanese
    if len(mkv.audio_tracks) > 1:
        audios = [audio for audio in mkv.audio_tracks if audio.language == settings.MASTER_LANG]
        if len(audios):
            raise PrintableException('Too audios in Japanese')
        if not len(audios):
            raise PrintableException('Too audios. None in Japanese')
        audio = audios[0]
    else:
        audio = mkv.audio_tracks[0]
    source = MkvSource(video)
    # Copiar solo el audio en japonés o el único que hay
    source.copy_audios(audio.number - 1)
    source.copy_videos('all')  # Copiar todos los vídeos
    mkvmerge = MkvMerge(dest)
    mkvmerge.add_source(source)  # Añadimos a nuestro archivo los datos copiados del original
    if len(subtitles) > 1:
        subtitles = settings.SUBTITLES_SORTED(subtitles)
    for i, subtitle in enumerate(subtitles):
        if hasattr(settings.SUBTITLES_DESCRIPTION, '__call__'):
            subtitle_description = settings.SUBTITLES_DESCRIPTION(video, dest, subtitle)
        else:
            subtitle_description = settings.SUBTITLES_DESCRIPTION
        mkvmerge.add_subtitle(subtitle, subtitle_description, settings.SUBTITLES_LANG, True if i is 0 else False)
    # Añadimos los subtítulos desde el directorio
    mkvmerge.add_attachments_from_dir(fonts_dir)
    if chapters is not None:
        mkvmerge.add_chapters(chapters, settings.SUBTITLES_LANG)
    mkvmerge.create()


def get_video_title(path):
    mkv = MKV(open(path, 'rb'))
    return mkv.info.title