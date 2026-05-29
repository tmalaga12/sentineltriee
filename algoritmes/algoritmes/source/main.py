# Programa principal de SentinelTrie.
# Uso:
#   python main.py <firmas.db> <ruta> [exacto|parcial]

import sys
from trie import Trie
from signature_db import cargar_firmas
from motor_escaneo import MotorExacto, MotorParcial
from escaner import escanear
from reporte import imprimir_informe


def main():
    if len(sys.argv) < 3:
        print("Uso: python main.py <firmas.db> <ruta> [exacto|parcial]")
        return

    archivo_firmas = sys.argv[1]
    ruta = sys.argv[2]
    modo = "exacto"
    if len(sys.argv) > 3:
        modo = sys.argv[3]

    # 1. Crear el trie y cargar las firmas
    trie = Trie()
    n = cargar_firmas(archivo_firmas, trie)
    print("Firmas cargadas:", n)

    # 2. Crear el motor segun el modo (polimorfismo)
    if modo == "parcial":
        motor = MotorParcial(trie, errores=1)
    else:
        motor = MotorExacto(trie)

    # 3. Escanear la ruta (recursivo si es carpeta)
    print("Escaneando", ruta, "...")
    resultados = escanear(motor, ruta)

    # 4. Imprimir informe
    imprimir_informe(resultados, modo)


if __name__ == "__main__":
    main()
