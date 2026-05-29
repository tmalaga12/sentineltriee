# Imprime el informe por pantalla.


def imprimir_informe(resultados, modo):
    print()
    print("---------------------------------------------")
    print(" INFORME SENTINELTRIE")
    print("---------------------------------------------")
    print(" Modo:", modo)
    print(" Archivos infectados:", len(resultados))
    total = 0
    for _, dets in resultados:
        total += len(dets)
    print(" Detecciones totales:", total)
    print("--------------------------------------------")
    if len(resultados) == 0:
        print(" No se han detectado amenazas.")
        return
    for archivo, dets in resultados:
        print()
        print(" [!]", archivo)
        for off, lg, nom, err in dets:
            extra = ""
            if err > 0:
                extra = " (+" + str(err) + " bytes mutados)"
            print("     ->", nom, "@", hex(off), "(", lg, "bytes )", extra)
    print()
