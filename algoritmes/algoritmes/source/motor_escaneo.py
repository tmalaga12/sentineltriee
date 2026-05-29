# Motores de escaneo. Herencia y polimorfismo:
#   Motor (base) -> MotorExacto, MotorParcial


class Motor:
    def __init__(self, trie):
        self.trie = trie
        self.nombre = "base"

    def analizar(self, datos):
        # cada subclase tiene que implementarlo
        raise NotImplementedError

    def escanear_archivo(self, ruta):
        try:
            f = open(ruta, "rb")
            datos = f.read()
            f.close()
        except Exception as e:
            print("No se ha podido leer", ruta, ":", e)
            return []
        return self.analizar(datos)


class MotorExacto(Motor):
    def __init__(self, trie):
        super().__init__(trie)
        self.nombre = "exacto"

    def analizar(self, datos):
        # devuelve lista de (offset, longitud, nombre, errores)
        resultados = []
        for off, lg, nom in self.trie.buscar_en_datos(datos):
            resultados.append((off, lg, nom, 0))
        return resultados


class MotorParcial(Motor):
    def __init__(self, trie, errores=1):
        super().__init__(trie)
        self.errores = errores
        self.nombre = "parcial"

    def _longitudes(self):
        # recorro el trie para saber que longitudes tienen las firmas
        L = set()
        self._rec(self.trie.raiz, 0, L)
        return sorted(L)

    def _rec(self, nodo, p, L):
        if nodo.final:
            L.add(p)
        for h in nodo.hijos.values():
            self._rec(h, p + 1, L)

    def analizar(self, datos):
        resultados = []
        vistos = set()
        for L in self._longitudes():
            if L == 0 or L > len(datos):
                continue
            for i in range(len(datos) - L + 1):
                ventana = datos[i:i+L]
                for nom in self.trie.buscar_aprox(ventana, self.errores):
                    clave = (i, nom)
                    if clave in vistos:
                        continue
                    vistos.add(clave)
                    resultados.append((i, L, nom, self.errores))
        return resultados
