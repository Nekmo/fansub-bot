import os
import subprocess
import zipfile
import tempfile
from create_video import VIDEO_PATTERN
from fields import DirMultiplesRootsWithRange
from nekbot import settings
from nekbot.core.commands import command
from nekbot.core.commands.control import control
from nekbot.core.types.filesystem import File, Dir
from plugins.premux import premux_video
from utils.files import search_by_pattern

__author__ = 'nekmo'

TEMP_DIR = os.path.join(tempfile.tempdir if tempfile.tempdir else '/tmp', 'nekbot')


SCRIPT_BASH = """\
#!/usr/bin/env bash

echo "Archivo generado con PatchMe 0.9.6.2"
echo
if [[ ! $(which xdelta3) ]]; then
	echo "No se encuentra el ejecutable de xdelta. Saliendo."
	exit -1
else
if [[ ! -f "{source}" ]]; then
        echo "No se encuentra el fichero de origen: {source}"
        exit -1
    fi

if [[ ! -f "file01.xdelta" ]]; then
        echo "No se encuentra el parche: file01.xdelta"
        exit -1
    fi

    echo "Parcheando el archivo: {source}"
    xdelta3 -f -d -s "{source}" "file01.xdelta" "{destination}"
    echo "Parche aplicado."

echo "Proceso finalizado."
fi

exit 0
"""


SCRIPT_BAT = """\
@echo off
chcp 65001>NUL
echo Archivo generado con PatchMe 0.9.6.2
echo.
if not exist "{source}" goto nofile
echo Parcheando el archivo: {source}
xdelta.exe -f -d -s "{source}" "file01.xdelta" "{destination}"
echo Parche aplicado.
echo.
echo Proceso finalizado.
pause
exit
:nofile
echo No se ha encontrado el archivo de origen en el directorio.
pause
exit
"""


def get_temp_file():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    return tempfile.NamedTemporaryFile(suffix='patch', dir=TEMP_DIR, delete=False)


def write_temp_file(content):
    f = get_temp_file()
    f.write(content)
    return f.name


def create_patch_script(content, source, destination):
    source = os.path.split(source)[1]
    destination = os.path.split(destination)[1]
    content = content.format(source=source, destination=destination)
    return write_temp_file(content)


def get_xdelta_path():
    import thirdparty
    return os.path.join(os.path.dirname(thirdparty.__file__), 'xdelta.exe')


def safe_list_get(l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default


@command('mkpatch', DirMultiplesRootsWithRange(settings.OWN_WORK_DIRECTORY, settings.FOREIGN_WORK_DIRECTORY),
         patch_sources=DirMultiplesRootsWithRange(settings.OWN_WORK_DIRECTORY, settings.FOREIGN_WORK_DIRECTORY))
@control('admin')
def mkpatch(msg, directories, patch_sources=()):
    for i, directory in enumerate(directories):
        path_with_crc = premux_video(msg, directory)
        patch_dir = os.path.join(directory, 'patch')
        if not os.path.exists(patch_dir):
            os.makedirs(patch_dir)
        patch_path = os.path.join(patch_dir, os.path.split(path_with_crc)[1] + '.zip')
        directory_video = safe_list_get(patch_sources, i, None)
        if directory_video is None:
            directory_video = directory
        video = os.path.join(directory, search_by_pattern(directory_video, VIDEO_PATTERN, 'videos'))
        create_patch(msg, video, path_with_crc, patch_path)


@command('patch', File(settings.FANSUB_ROOT), File(settings.FANSUB_ROOT), Dir(settings.FANSUB_ROOT))
def patch(msg, source, target, dest_dir):
    filename = os.path.split(target)[1]
    patch_path = os.path.join(dest_dir, filename) + '.zip'
    create_patch(msg, source, target, patch_path, False)


def create_patch(msg, video, target, patch_path, remove_video=True):
    delta_path = get_temp_file().name
    zipf = zipfile.ZipFile(patch_path, 'w')
    script_bash = create_patch_script(SCRIPT_BASH, video, target)
    script_bat = create_patch_script(SCRIPT_BAT, video, target)
    sp = subprocess.Popen(['xdelta3', '-f', '-s', video, target, delta_path],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = sp.communicate()
    zipf.write(script_bash, 'unix.sh')
    zipf.write(script_bat, 'windows.bat')
    zipf.write(delta_path, 'file01.xdelta')
    zipf.write(get_xdelta_path(), 'xdelta.exe')
    if sp.returncode == 0:
        msg.reply('Created patch in %s' % patch_path, notice=True)
    else:
        msg.reply('Error creating patch. Stdout: %s Stderr: %s' % (
            stdout.replace('\n', ' ') if stdout else '--', stderr.replace('\n', '') if stderr else '--'))
    for remove in [script_bash, script_bat, delta_path, target]:
        if remove == target and not remove_video:
            continue
        os.remove(remove)
