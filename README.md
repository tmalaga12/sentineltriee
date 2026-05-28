
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

### Lectura de archivos: MVP vs sistema real

**En este MVP** la lectura es **on-demand y síncrona**: el usuario lanza la CLI contra un archivo o un directorio, `Escaner._recorrer()` hace un DFS recursivo y para cada archivo `MotorEscaneo.escanear_archivo()` abre el archivo en modo binario, lo carga entero en memoria (con un cap de 10 MB para evitar consumos descontrolados) y se lo pasa al motor. No hay descarga remota: las firmas y los archivos a escanear están ya en disco.

**En un sistema real de producción** la lectura sería **on-access**, interceptando eventos del sistema operativo:
- **Linux:** API `fanotify` para interceptar `open`/`exec` y bloquear el archivo hasta que se haya escaneado.
- **Windows:** un **minifilter driver** que se engancha al subsistema de archivos del kernel (es el modelo que usa Microsoft Defender).
- **macOS:** el `Endpoint Security framework`.

Para archivos grandes (> 100 MB) se usaría `mmap` y escaneo por bloques manteniendo el estado del Trie entre lecturas — está recogido en las propuestas de mejora del `estudi_complexitat.pdf`.

### Fuentes de firmas

**En el MVP** las firmas viven en `data/signatures/signatures.db`, un archivo de texto cargado al arrancar por `GestorFirmas.cargar_desde_archivo()`. Contiene una firma oficial del sector (EICAR) y 17 firmas sintéticas diseñadas por nosotros para demostrar el ahorro por prefijos compartidos.

**En un sistema real** se alimentaría desde feeds públicos descargados periódicamente:

| Fuente | URL | Qué aporta |
|---|---|---|
| abuse.ch MalwareBazaar | bazaar.abuse.ch | Hashes y muestras de malware reciente (API REST gratuita) |
| abuse.ch URLhaus | urlhaus.abuse.ch | URLs maliciosas |
| abuse.ch ThreatFox | threatfox.abuse.ch | IoCs (Indicators of Compromise) |
| ClamAV CVD | clamav.net | Firmas oficiales de ClamAV (`freshclam`) |
| YARA-Rules | github.com/Yara-Rules/rules | Reglas comunitarias |
| MISP | misp-project.org | Feeds compartidos entre organizaciones |

`GestorFirmas` es agnóstico al origen: cualquier feed se puede normalizar al formato `nombre:HEX`.
### Identificación de patrones detectados

Cada firma se inserta en el Trie con un nombre legible (`NodoTrie.nombre_firma`). Cuando un escaneo encuentra una coincidencia se construye un `Deteccion(archivo, firma, offset, longitud, tipo_escaneo, errores)`. El `offset` se reporta en hexadecimal para que sea verificable manualmente con un editor hex. El informe final agrupa por archivo:

```
[!] /home/user/Downloads/sospechoso.bin
     -> Trojan.Generic.A @ offset 0x000000c8 (8B) (exacto)
     -> Ransomware.Lockbit.Stub @ offset 0x00000198 (8B) (exacto)
```

### Tiempos esperados según el alcance

Medidos sobre nuestro código (ver `tests/benchmark.py`):

| Alcance | Tamaño | Firmas | Tiempo (exacto) |
|---|---|---|---|
| Carpeta `test_files` de la demo | 9,8 KB | 18 | ~16 ms |
| Archivo de 100 KB | 100 KB | 500 | ~23 ms |
| Archivo de 1 MB | 1 MB | 5.000 | ~274 ms (vs 935 ms lineal) |
| Carpeta `Downloads` típica (estimado) | ~500 MB / 500 archivos | 5.000 | 5–30 s |

El motor parcial (`--max-errores 1`) es del orden de **10× más lento** que el exacto porque para cada longitud de firma realiza una ventana deslizante con backtracking. Es razonable usarlo como segunda pasada solo sobre archivos sospechosos, no como motor principal.

## Instrucciones de ejecución y dependencias

### Requisitos

- **Python 3.10 o superior** (usamos `match-case`, anotaciones `X | None` y `dataclasses`).
- Solo la **biblioteca estándar** para el motor en sí. `reportlab` solo se usó para generar los PDFs de la documentación (ya incluidos en `/docs`, no es necesaria su instalación).

### Generar los archivos de prueba (primera vez)

```bash
python data/generar_test_files.py
```

Esto crea `data/test_files/` con archivos limpios y archivos sintéticos infectados.

### Ejecutar un escaneo (modo exacto)

```bash
cd source
python main.py --firmas ../data/signatures/signatures.db \
               --objetivo ../data/test_files
```
### Ejecutar en modo parcial (tolerante a mutaciones)

```bash
python main.py --firmas ../data/signatures/signatures.db \
               --objetivo ../data/test_files \
               --modo parcial --max-errores 1
```

### Exportar informe JSON

```bash
python main.py --firmas ../data/signatures/signatures.db \
               --objetivo ../data/test_files \
               --json informe.json
```

### Filtrar por extensiones

```bash
python main.py --firmas ../data/signatures/signatures.db \
               --objetivo /ruta/grande --ext .exe,.dll,.bin
```

### Tests y benchmarks

```bash
# 9 tests unitarios
python tests/test_trie.py

# Benchmark Trie vs. lineal — genera tests/benchmark_results.csv
python tests/benchmark.py
```
## Estructura del repositorio

```
.
├── README.md
├── data/
│   ├── generar_test_files.py
│   ├── signatures/
│   │   └── signatures.db
│   └── test_files/                  # generados por generar_test_files.py
├── docs/
│   ├── uml.svg
│   ├── flux_F1_carga_firmas.svg
│   ├── flux_F2_escaneo_multimodal.svg
│   ├── flux_F3_navegacion_directorios.svg
│   ├── flux_F4_reporte_amenazas.svg
│   ├── estudi_complexitat.pdf
│   └── conclusions_i_propostes_futur.pdf
├── source/
│   ├── trie.py             # Trie + NodoTrie (recursión)
│   ├── signature_db.py     # GestorFirmas
│   ├── motor_escaneo.py    # MotorEscaneo + 2 subclases (polimorfismo)
│   ├── escaner.py          # Escaner (DFS recursivo)
│   ├── reporte.py          # GeneradorReporte
│   └── main.py             # CLI
└── tests/
    ├── test_trie.py        # 9 tests unitarios
    └── benchmark.py        # benchmark Trie vs. lineal
```
### Códigos de salida (estilo antivirus)

- `0` — Sin amenazas detectadas.
- `1` — Se han encontrado archivos infectados o hubo error de carga.
