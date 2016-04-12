# coding=utf-8
import logging
import os
import sys
import zlib

__author__ = 'nekmo'

#Colores
c_null  = "\x1b[00;00m"
c_red   = "\x1b[31;01m"
c_green = "\x1b[32;01m"
p_reset = "\x08"*8


def get_crc32(filename, show_progress=True):
    """Generador del CRC del archivo
       filename: string
                 Ruta al archivo"""

    # Variables para comprobación
    crc = 0
    file = open(filename, "rb")
    buff_size = 65536
    size = os.path.getsize(filename)
    done = 0

    if not size:
        # El archivo no tiene tamaño, salir
        logging.error('El archivo %s no tiene datos' % filename)
        return
    try:
        while True:
            # Mientras haya datos...
            data = file.read(buff_size)
            done += buff_size
            if show_progress:
                # informar de situación actual de conteo
                if show_progress:
                    sys.stdout.write("%7d"%(done*100/size) + "%" + p_reset)
            if not data:
                # Ya no hay más datos, salir
                break
            crc = zlib.crc32(data, crc)
    except KeyboardInterrupt:
        # Detectada excepción de interrupción por teclado
        if show_progress:
            sys.stdout.write(p_reset)
        # Cerrar el archivo
        file.close()
        sys.exit(1)
    if show_progress:
        sys.stdout.write("")
    file.close()
    # Cálculo
    if crc < 0:
        crc &= 2**32-1
    return "%.8X" %(crc)