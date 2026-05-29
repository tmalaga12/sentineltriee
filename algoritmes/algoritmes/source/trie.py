# Arbol Trie para guardar firmas de virus byte a byte.
# Para diseñar la busqueda aproximada con backtracking (funciones  buscar_aprox y _aprox) nos hemos ayudado con la IA 
# para entender bien la idea de las dos ramas de recursion (coincidencia
# exacta vs gasto de error). 


class Nodo:
    def __init__(self):
        self.hijos = {}
        self.final = False
        self.nombre = None


class Trie:
    def __init__(self):
        self.raiz = Nodo()
        self.n_firmas = 0

    # Insercion recursiva
    def insertar(self, firma, nombre):
        self._insertar(self.raiz, firma, 0, nombre)
        self.n_firmas += 1

    def _insertar(self, nodo, firma, i, nombre):
        if i == len(firma):
            nodo.final = True
            nodo.nombre = nombre
            return
        b = firma[i]
        if b not in nodo.hijos:
            nodo.hijos[b] = Nodo()
        self._insertar(nodo.hijos[b], firma, i + 1, nombre)

    # Busqueda exacta de una firma completa
    def buscar(self, firma):
        return self._buscar(self.raiz, firma, 0)

    def _buscar(self, nodo, firma, i):
        if i == len(firma):
            if nodo.final:
                return nodo.nombre
            return None
        b = firma[i]
        if b not in nodo.hijos:
            return None
        return self._buscar(nodo.hijos[b], firma, i + 1)

    # Busca todas las firmas que aparecen dentro de "datos"
    def buscar_en_datos(self, datos):
        encontrados = []
        for i in range(len(datos)):
            nodo = self.raiz
            j = i
            while j < len(datos) and datos[j] in nodo.hijos:
                nodo = nodo.hijos[datos[j]]
                j += 1
                if nodo.final:
                    encontrados.append((i, j - i, nodo.nombre))
        return encontrados

    # Busqueda aproximada: hasta "errores" bytes diferentes.
    # Esta es la parte que mas nos ha costado del proyecto y nos
    # hemos ayudado de la IA para entender el patron de backtracking
    # con dos ramas (bajar por byte que coincide y probar otros gastando
    # un error). El resultado lo hemos validado con los tests
    def buscar_aprox(self, patron, errores):
        res = []
        self._aprox(self.raiz, patron, 0, errores, res)
        return res

    def _aprox(self, nodo, patron, i, errores, res):
        if i == len(patron):
            if nodo.final:
                res.append(nodo.nombre)
            return
        if errores < 0:
            return
        b = patron[i]
       
        if b in nodo.hijos:
            self._aprox(nodo.hijos[b], patron, i + 1, errores, res)
        
        if errores > 0:
            for k in nodo.hijos:
                if k != b:
                    self._aprox(nodo.hijos[k], patron, i + 1, errores - 1, res)
