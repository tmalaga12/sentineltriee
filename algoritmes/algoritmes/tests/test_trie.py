# Pruebas basicas. Ejecutar con:  python tests/test_trie.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "source"))

from trie import Trie
from motor_escaneo import MotorExacto, MotorParcial


def test_insertar_y_buscar():
    t = Trie()
    t.insertar(b"\xde\xad\xbe\xef", "Trojan.A")
    assert t.buscar(b"\xde\xad\xbe\xef") == "Trojan.A"
    assert t.buscar(b"\xde\xad") is None
    print("OK - test_insertar_y_buscar")


def test_buscar_en_datos():
    t = Trie()
    t.insertar(b"ABC", "F1")
    t.insertar(b"DEF", "F2")
    datos = b"XXABCDEFXX"
    res = t.buscar_en_datos(datos)
    nombres = sorted([r[2] for r in res])
    assert nombres == ["F1", "F2"]
    print("OK - test_buscar_en_datos")


def test_buscar_aprox():
    t = Trie()
    t.insertar(b"\x4d\x5a\x90\x00", "PE")
    # cambiamos un byte
    res = t.buscar_aprox(b"\x4d\x5a\x91\x00", 1)
    assert "PE" in res
    # con 0 errores ya no
    res2 = t.buscar_aprox(b"\x4d\x5a\x91\x00", 0)
    assert res2 == []
    print("OK - test_buscar_aprox")


def test_polimorfismo():
    t = Trie()
    t.insertar(b"VIRUS", "X")
    motores = [MotorExacto(t), MotorParcial(t, errores=1)]
    for m in motores:
        # los dos tienen el mismo metodo (polimorfismo)
        r = m.analizar(b"hola VIRUS adios")
        assert len(r) >= 1
    print("OK - test_polimorfismo")


def test_motor_parcial_detecta_mutado():
    t = Trie()
    t.insertar(b"VIRUS", "X")
    exacto = MotorExacto(t)
    parcial = MotorParcial(t, errores=1)
    # cambiamos un byte
    datos = b"hola VIRuS adios"
    assert exacto.analizar(datos) == []
    assert len(parcial.analizar(datos)) >= 1
    print("OK - test_motor_parcial_detecta_mutado")


if __name__ == "__main__":
    test_insertar_y_buscar()
    test_buscar_en_datos()
    test_buscar_aprox()
    test_polimorfismo()
    test_motor_parcial_detecta_mutado()
    print()
    print("Todos los tests pasan.")
