
# SentinelTrie

Motor de detección de malware por firmas basado en Árbol Trie. Escanea archivos en busca de secuencias de bytes maliciosas usando un motor multi-patrón en O(m) que reemplaza al escaneo lineal O(N·m), permitiendo procesar miles de firmas simultáneamente sin penalización proporcional al tamaño de la base de datos.

> Disseny i Anàlisi d'Algoritmes Avançats — ENTI-UB — Grado en Ciberseguridad

## Integrantes del grupo

- Antonio Málaga
- Max Mora

## Contexto y problemática

Los antivirus tradicionales que utilizan **escaneo lineal por firmas** sufren un problema fundamental de escalado: cada firma añadida a la base de datos incrementa proporcionalmente el coste del escaneo. Con bases de datos modernas que rondan el millón de firmas, el escaneo en tiempo real se vuelve inviable. Además, el **malware polimórfico** muta unos pocos bytes en cada infección, lo que basta para evadir un matching exacto.

SentinelTrie aborda ambos problemas con una única estructura de datos: el **Árbol Trie** (árbol de prefijos). Esta misma técnica es la que utilizan internamente herramientas industriales como **ClamAV**, **Snort/Suricata** (vía Aho-Corasick, una extensión del Trie) y los motores de **YARA**. El proyecto reproduce el principio fundamental en un entorno académico, demostrando empíricamente la mejora de complejidad respecto al enfoque ingenuo.

## Funcionalidades principales

| | Funcionalidad | Descripción |
|---|---|---|
| F1 | Carga de base de datos | Importa firmas desde un archivo `signatures.db` (formato `nombre:HEX`) y las inserta recursivamente en el Trie. |
| F2 | Escaneo multimodal | Dos motores polimórficos: **exacto** (matching idéntico, O(m)) y **parcial** (tolerante a `N` bytes mutados, backtracking). |
| F3 | Navegación de directorios | Recorrido recursivo (DFS) del sistema de archivos, con filtrado por extensión y manejo seguro de symlinks y permisos. |
| F4 | Reporte de amenazas | Informe legible en consola con colores ANSI **y** exportación a JSON estructurado para integraciones posteriores. |

## Uso de POO y polimorfismo

El sistema está diseñado en torno a una **jerarquía polimórfica de motores de escaneo**. Las clases principales son:

- **`MotorEscaneo`** (`source/motor_escaneo.py`) — Clase **abstracta** (`ABC`). Define la interfaz común con el método abstracto `analizar(datos, archivo)` y el método compartido `escanear_archivo(archivo)` (patrón Template Method).
- **`EscaneoFirmaExacta`** — Subclase concreta que reimplementa `analizar()` haciendo coincidencia exacta byte a byte mediante `Trie.buscar_en_datos()`.
- **`EscaneoFirmaParcial`** — Subclase concreta que reimplementa `analizar()` con backtracking recursivo tolerante a mutaciones (`Trie.buscar_aproximado()`).

**Dónde aparece el polimorfismo concretamente:**

1. En `source/escaner.py`, la clase `Escaner` recibe un `MotorEscaneo` por inyección de dependencia y nunca pregunta de qué subclase se trata — simplemente invoca `self.motor.escanear_archivo(...)`. El comportamiento real depende del objeto pasado.
2. En `source/main.py`, la función `construir_motor()` es el único lugar del programa que conoce las subclases concretas: según `--modo` instancia una u otra, y devuelve el objeto tipado como `MotorEscaneo`. El resto de `main()` lo trata como interfaz.
3. En `tests/test_trie.py`, el test `test_motores_misma_interfaz` itera explícitamente sobre una lista mixta `[EscaneoFirmaExacta(...), EscaneoFirmaParcial(...)]` invocando los mismos métodos sobre cada instancia.

Otras clases del sistema:

- **`Trie` y `NodoTrie`** (`source/trie.py`) — Estructura de datos central, con inserción y búsqueda recursivas.
- **`GestorFirmas`** (`source/signature_db.py`) — Encapsula la carga de la base de datos.
- **`Escaner`** (`source/escaner.py`) — Orquesta el recorrido recursivo del sistema de archivos.
- **`GeneradorReporte`** (`source/reporte.py`) — Genera salida humana y JSON.
- **`Deteccion`, `ResultadoEscaneo`** — Dataclasses inmutables del dominio.
## Modelo de datos: lectura de archivos y fuentes de firmas

Esta sección responde explícitamente a las preguntas planteadas durante la revisión de la Fase 1 sobre cuándo se leen los archivos, de dónde se obtienen las firmas, cómo se identifican los matches y los tiempos esperados según el alcance.

