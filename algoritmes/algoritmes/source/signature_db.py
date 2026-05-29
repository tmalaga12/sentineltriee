# Carga el archivo de firmas y las mete en el trie.


def cargar_firmas(ruta, trie):
    n = 0
    f = open(ruta, "r", encoding="utf-8")
    for linea in f:
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue
        if ":" not in linea:
            print("Linea ignorada:", linea)
            continue
        nombre, hex_str = linea.split(":", 1)
        nombre = nombre.strip()
        hex_str = hex_str.strip().replace(" ", "")
        try:
            firma = bytes.fromhex(hex_str)
        except ValueError:
            print("Hex invalido en:", nombre)
            continue
        if len(firma) == 0:
            continue
        trie.insertar(firma, nombre)
        n += 1
    f.close()
    return n
