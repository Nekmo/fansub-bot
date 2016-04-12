# coding=utf-8
import os
import re


IRC_AUTHS = {
    # Cómo debe autenticarse el bot.
    'servidor.com': {'username': 'NombreBot', 'realname': 'FansubBot'},
}

IRC_GROUPCHATS = [
    'mifansub@servidor.com', # Salas a las que entrará
]

IRC_PERMISSIONS = {
    'owerbot@servidor.com': ['root'], # Quien puede hacer cualquier cosa
    'admin@servidor.com': ['admin'], # Quien puede ejecutar los comandos de fansub
}

VIDEO_NAME_PROCESSORS = [
]

FANSUB_NAME = 'Fansub Name'
# El nombre que aparece entre los primeros corchetes en nuestras releases
FANSUB_SHORT_NAME = 'FansubName'
FANSUB_ROOT = '/home/fansub/Works'
# Es el directorio del que parten los directorios con las series en trabajo.
WORK_DIRECTORY = os.path.join(FANSUB_ROOT, 'premux')
# Tenemos 2 directorios dentro de WORK_DIRECTORY: una con los trabajos propios, y otra
# con los trabajos que se realizan en conjunto con otros fansubs (colaboraciones).
# Dentro de los mismos, la estructura es la misma: <Nombre Serie>/<capítulo>/<archivos>,
# donde archivos, son el mkv del que tomar el audio y vídeo, el archivo .ass/.ssa, y
# un directorio "fonts" con las fuentes a adjuntar en el archivo destino.
# Ejemplo:
# /home/fansub/Works/premux/ <-- Raíz de WORK_DIRECTORY (directorio de proyectos)
# /home/fansub/Works/premux/Fansub Name/ <-- Directorio
# /home/fansub/Works/premux/Fansub Name/serie/02/ <-- Fuentes para serie, capítulo 02
# /home/fansub/Works/premux/Fansub Name/serie/02/[FansubName]video.mkv <-- Del que obtener audio/vídeo
# /home/fansub/Works/premux/Fansub Name/serie/02/subs.ass <-- Subtítulos a poner
# /home/fansub/Works/premux/Fansub Name/serie/02/fonts/ <-- Directorio con fuentes
OWN_WORK_DIRECTORY = os.path.join(WORK_DIRECTORY, FANSUB_NAME)
# Lo mismo que con OWN_WORK_DIRECTORY, pero cambiando Fansub Name por "Otros".
FOREIGN_WORK_DIRECTORY = os.path.join(WORK_DIRECTORY, 'Otros')
RELEASES_DIRECTORY = os.path.join(FANSUB_ROOT, 'xdcc', 'XDCC')
# Si el archivo compilado viene del directorio OWN_WORK_DIRECTORY, será almacenado en este
# directorio, y se le cambiará el tag inicial ([FansubName) para que sea el de nuestro
# fansub.
OWN_RELEASES = os.path.join(RELEASES_DIRECTORY, 'FansubName')
# Si el archivo compilado viene del directorio FOREIGN_WORK_DIRECTORY, será almacenado en
# este directorio, y se conservará el tag inicial
FOREIGN_RELEASES = os.path.join(RELEASES_DIRECTORY, 'Otros')
FONTS_DIR_PATTERN = re.compile('fonts')
MASTER_LANG = 'jpn'
SUBTITLES_LANG = 'spa'
SUBTITLES_DESCRIPTION = "Descripción a mostrar en los archivos de subtítulos."
TAGS_TO_REMOVE= [
    re.compile('\[premux\]', re.IGNORECASE),
]