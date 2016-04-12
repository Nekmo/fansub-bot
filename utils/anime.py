# coding=utf-8
import re
import shutil
from nekbot.core.exceptions import PrintableException
from utils.crc import get_crc32
from utils.files import remove_extension, split_extension
from utils.strings import rreplace

__author__ = 'nekmo'


def remove_crc(filename):
    """Remove only last CRC ([ABCD1234]) in filename
    """
    crcs = re.findall('(\[[A-Fa-f0-9]{8}\])', filename)
    if not crcs:
        return filename
    return rreplace(filename, crcs[-1], '', 1)


def remove_brackets(text):
    """Remove all between brackets.

    "[A] Text[B]![C]" -> " Text!"
    """
    return re.sub('\[([^\]]+)\]', '', text)


def get_episodes(filename):
    filename = remove_extension(filename)
    filename = remove_brackets(filename)
    # Elimino los números de versiones (hasta vers. 6)
    filename = re.sub('(.+\d{1,3})v[1-6]', r'\1', filename)
    episodes = re.findall('(\d{2,3}\-\d{2,3})', filename)
    if not len(episodes):
        # Busco por un capítulo de 2-3 cifras
        episodes = re.findall('(\d{2,3})', filename)
        if not len(episodes):
            # Sigo sin tener suerte. Pruebo con 1 cifra
            episodes = re.findall('(\d{1})', filename)
    if not len(episodes):
        return None
    episodes = episodes[-1]
    if not isinstance(episodes, (list, tuple)):
        return int(episodes)
    return map(int, episodes)


def remove_episode(filename):
    """Una lógica harto laboriosa para eliminar solo el número del capítulo en el
    nombre del archivo. Preferible capítulos de 2-3 dígitos. Elimina sólo la
    última aparición. Tiene en cuenta las versiones (pj. 04v2), además de los
    capítulos dobles (04-06). Ignora todo entre corchetes.
    """
    # Elimino los números de versiones (hasta vers. 6)
    filename = re.sub('(.+\d{1,3})v[1-6]', r'\1', filename)
    filename_no_brackets = remove_brackets(filename)
    # Elimino la extensión del archivo en filename_no_brackets
    filename_no_brackets = remove_extension(filename_no_brackets)
    orig_filename_no_brackets = filename_no_brackets
    # Compruebo si el nombre del archivo (sin corchetes) acaba por alguno de los
    # caracteres a eliminar al final. Si es así, lo tomo para volver a ponerlo
    # al final
    end_filename = re.findall('([ \-_]+)$', filename_no_brackets)
    end_filename = end_filename[0] if end_filename else ''
    # Busco si es un capítulo doble
    double_episode = re.findall('(\d{2,3}\-\d{2,3})', filename_no_brackets)
    if len(double_episode):
        # Reemplazo el cap doble
        filename_no_brackets = rreplace(filename_no_brackets, double_episode[-1], '', 1)
    else:
        # Busco por un capítulo de 2-3 cifras
        episode = re.findall('(\d{2,3})', filename_no_brackets)
        if len(episode):
            filename_no_brackets = rreplace(filename_no_brackets, episode[-1], '', 1)
        else:
            # Sigo sin tener suerte. Pruebo con 1 cifra
            episode = re.findall('(\d{1})', filename_no_brackets)
            if len(episode): filename_no_brackets = rreplace(filename_no_brackets, episode[-1], '', 1)
    while True:
        # Elimino caracteres innecesarios del final
        if not filename_no_brackets[-1] in [' ', '-', '_']: break
        filename_no_brackets = filename_no_brackets[:-1]
    # Reemplazo del nombre el filename_no_brackets final con el original
    filename = filename.replace(orig_filename_no_brackets, filename_no_brackets + end_filename)
    return filename


def get_short_name(filename):
    """Get first label between brackets in text (without '[' and ']')
    """
    try:
        return re.match('^\[([^\]]+)\].+$', filename).group(1)
    except Exception as e:
        raise PrintableException('The video file has not short name')


def remove_short_name_tag(filename):
    try:
        short_name = get_short_name(filename)
    except PrintableException:
        return filename
    return re.sub('\[%s\]' % short_name, '', filename, 1, re.IGNORECASE)


def set_crc(path):
    crc = get_crc32(path, False)
    path_without_ext, ext = split_extension(path)
    path_without_ext = '%s[%s]' % (path_without_ext, crc)
    path_with_crc = '.'.join([path_without_ext, ext])
    shutil.move(path, path_with_crc)
    return path_with_crc