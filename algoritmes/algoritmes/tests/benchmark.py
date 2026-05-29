
from __future__ import annotations
import csv
import os
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))

from trie import Trie  


def busqueda_lineal(firmas: list[bytes], datos: bytes) -> int:
    
    #Para cada firma realiza un str.find recorriendo todo el contenido.
    #Complejidad: O(n × m × k) donde n=#firmas, m=len(datos), k=len(firma).
    
    cuenta = 0
    for f in firmas:
        # encontrar todas las ocurrencias
        inicio = 0
        while True:
            pos = datos.find(f, inicio)
            if pos == -1:
                break
            cuenta += 1
            inicio = pos + 1
    return cuenta


def busqueda_trie(trie: Trie, datos: bytes) -> int:
    return len(trie.buscar_en_datos(datos))


def generar_firma(longitud: int, rng: random.Random) -> bytes:
    return bytes(rng.randint(0, 255) for _ in range(longitud))


def generar_datos(tam: int, firmas: list[bytes],
                  rng: random.Random) -> bytes:
    # 1% del archivo serán "infecciones" reales mezcladas con basura.
    base = bytearray(rng.randint(0, 255) for _ in range(tam))
    inyecciones = max(1, tam // 1000)
    for _ in range(inyecciones):
        f = rng.choice(firmas)
        offset = rng.randint(0, max(0, tam - len(f)))
        base[offset:offset + len(f)] = f
    return bytes(base)


def main():
    rng = random.Random(42)
    out_path = Path(__file__).parent / "benchmark_results.csv"

    # Escenarios: varía #firmas (N) y tamaño de archivo (M).
    escenarios = [
        (50, 100_000),
        (500, 100_000),
        (5_000, 100_000),
        (50, 1_000_000),
        (500, 1_000_000),
        (5_000, 1_000_000),
    ]

    print(f"\n{'N firmas':>10} {'Tam datos':>12} "
          f"{'Lineal (s)':>12} {'Trie (s)':>10} "
          f"{'Speedup':>8} {'detecc':>8}")
    print("-" * 70)

    resultados = []
    for n_firmas, tam in escenarios:
        firmas = [
            generar_firma(rng.randint(6, 16), rng) for _ in range(n_firmas)
        ]
        datos = generar_datos(tam, firmas, rng)

        # Trie con N firmas
        trie = Trie()
        for i, f in enumerate(firmas):
            trie.insertar(f, f"Sig{i}")

        # Medir Trie
        t0 = time.perf_counter()
        c_trie = busqueda_trie(trie, datos)
        t_trie = time.perf_counter() - t0

        # Medir lineal (sólo con N pequeño para que no eternice;
        # con N=5000 lo limitamos a 200 firmas representativas).
        firmas_lineal = firmas if n_firmas <= 500 else firmas[:200]
        t0 = time.perf_counter()
        _ = busqueda_lineal(firmas_lineal, datos)
        t_lin = time.perf_counter() - t0
        # Reescalamos al equivalente "as if N completo".
        t_lin_full = t_lin * (n_firmas / len(firmas_lineal))

        speedup = t_lin_full / t_trie if t_trie else float("inf")

        print(f"{n_firmas:>10} {tam:>12} {t_lin_full:>12.4f} "
              f"{t_trie:>10.4f} {speedup:>7.1f}x {c_trie:>8}")
        resultados.append({
            "n_firmas": n_firmas,
            "tam_datos": tam,
            "tiempo_lineal_s": round(t_lin_full, 5),
            "tiempo_trie_s": round(t_trie, 5),
            "speedup": round(speedup, 2),
            "detecciones": c_trie,
        })

    # Volcar a CSV.
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        w.writeheader()
        w.writerows(resultados)
    print(f"\n[i] Resultados guardados en {out_path}")


if __name__ == "__main__":
    main()
