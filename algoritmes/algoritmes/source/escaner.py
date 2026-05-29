# Recorre directorios de forma recursiva y aplica el motor a cada archivo.

import os


def escanear(motor, ruta):
    resultados = []
    if os.path.isfile(ruta):
        dets = motor.escanear_archivo(ruta)
        if dets:
            resultados.append((ruta, dets))
        return resultados
    # si no es archivo, asumo que es directorio
    _recorrer(motor, ruta, resultados)
    return resultados


def _recorrer(motor, directorio, resultados):
    try:
        entradas = os.listdir(directorio)
    except PermissionError:
        return
    for nombre in entradas:
        camino = os.path.join(directorio, nombre)
        if os.path.islink(camino):
            continue
        if os.path.isdir(camino):
            _recorrer(motor, camino, resultados)
        elif os.path.isfile(camino):
            dets = motor.escanear_archivo(camino)
            if dets:
                resultados.append((camino, dets))
