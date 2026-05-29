# generar_test_files.py
# Crea archivos de prueba (limpios e infectados) en data/test_files.

import os
import random

BASE = os.path.join(os.path.dirname(__file__), "test_files")
SUB = os.path.join(BASE, "subcarpeta")

EICAR = (b"X5O!P%@AP[4\\PZX54(P^)7CC)7}"
         b"$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
TROJAN = bytes.fromhex("DEADBEEFCAFEBABE")
LOCKBIT = bytes.fromhex("4C4F434B42495445")
MIRAI = bytes.fromhex("4D495241494C4F47494E")
TROJAN_MUT = bytes.fromhex("DEADBEEFCAFEBA00")  # 1 byte cambiado


def basura(n):
    random.seed(7)  # para que sea reproducible
    return bytes(random.randint(0, 255) for _ in range(n))


def main():
    if not os.path.exists(BASE):
        os.makedirs(BASE)
    if not os.path.exists(SUB):
        os.makedirs(SUB)

    # archivos limpios
    open(os.path.join(BASE, "limpio_1.bin"), "wb").write(basura(1024))
    open(os.path.join(BASE, "limpio_2.bin"), "wb").write(basura(2048))
    open(os.path.join(BASE, "documento.txt"), "w").write(
        "Texto inocuo de prueba.\n"
    )

    # archivo con un troyano
    open(os.path.join(BASE, "infectado_trojan.bin"), "wb").write(
        basura(300) + TROJAN + basura(300)
    )

    # archivo con eicar
    open(os.path.join(BASE, "infectado_eicar.txt"), "wb").write(
        b"cabecera\n" + EICAR + b"\nfinal\n"
    )

    # archivo con varias firmas
    contenido = (basura(100) + TROJAN + basura(100) + LOCKBIT
                 + basura(100) + MIRAI + basura(100))
    open(os.path.join(BASE, "infectado_varios.bin"), "wb").write(contenido)

    # archivo mutado (solo detectable en modo parcial)
    open(os.path.join(BASE, "mutado_trojan.bin"), "wb").write(
        basura(200) + TROJAN_MUT + basura(200)
    )

    # archivo dentro de subcarpeta (para probar la recursion)
    open(os.path.join(SUB, "anidado_infectado.bin"), "wb").write(
        basura(50) + LOCKBIT + basura(50)
    )

    print("Archivos de prueba creados en", BASE)


if __name__ == "__main__":
    main()
