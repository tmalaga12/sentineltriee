
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

