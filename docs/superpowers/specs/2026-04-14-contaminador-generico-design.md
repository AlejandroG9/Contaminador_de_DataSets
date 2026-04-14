# Diseño: Contaminador de Dataset Genérico

**Fecha:** 2026-04-14  
**Proyecto:** Contaminador de Datos — Ingeniería de la Información  
**Objetivo:** Adaptar el contaminador para funcionar con cualquier CSV via CLI, sin hardcodear nombres de columnas.

---

## Contexto

El proyecto actual contamina intencionalmente el dataset `social_media_mental_health.csv` con 7 tipos de problemas de calidad de datos, para que los alumnos los detecten y limpien. El problema es que todos los `caso*.py` tienen los nombres de columnas hardcodeados, lo que hace imposible reutilizarlos con otros datasets sin reescribir el código.

---

## Solución: Enfoque A — Detección automática por tipo de columna

Refactorizar la clase existente y cada caso para que operen sobre columnas detectadas automáticamente según su tipo, sin configuración manual.

---

## Arquitectura

### 1. CLI con `argparse`

Se agrega un punto de entrada por línea de comandos al mismo archivo `contaminar_dataset.py`:

```bash
# Uso mínimo
python contaminar_dataset.py mi_dataset.csv

# Uso completo
python contaminar_dataset.py mi_dataset.csv --salida resultado.csv --porcentaje 0.15 --casos 1 3 5 7 --encoding latin-1
```

**Argumentos:**
- `archivo` (posicional, requerido) — ruta al CSV de entrada
- `--salida` (opcional) — ruta de salida; por defecto `<nombre>_contaminado.csv`
- `--porcentaje` (opcional, default `0.10`) — fracción de registros a contaminar por caso
- `--casos` (opcional, default todos) — enteros del 1 al 7, p.ej. `--casos 1 3 5`. Se convierten internamente a `['caso1', 'caso3', 'caso5']` antes de pasar a `contaminar_dataset()`.
- `--encoding` (opcional, default `utf-8`) — encoding del CSV; usar `latin-1` para archivos con caracteres especiales no-UTF-8. Si el encoding es inválido o no coincide con el archivo, el CLI captura el `UnicodeDecodeError` y muestra un mensaje claro: `"Error al leer el archivo: encoding incorrecto. Prueba con --encoding latin-1"`.

### 2. Detección automática de columnas en `ContaminadorDataset`

Nuevo método `_detectar_columnas()` llamado automáticamente al cargar el dataset. Clasifica columnas en 5 grupos. **Todos los matches de nombres de columna son case-insensitive** (se normaliza con `.lower()` antes de comparar):

| Grupo | Criterio de detección |
|-------|----------------------|
| `cols_ids` | dtype `object` con proporción de valores únicos > 80% del total de filas |
| `cols_categoricas` | dtype `object` que no son IDs |
| `cols_binarias` | dtype numérico cuyos valores únicos son exactamente `{0, 1}` |
| `cols_horas` | dtype numérico (no binaria) cuyo nombre contiene "hour", "hora" o "time" |
| `cols_numericas` | dtype numérico que no es binaria ni de horas |

Las columnas binarias (`cols_binarias`) se excluyen de `cols_numericas` y `cols_horas` para evitar contaminaciones sin sentido pedagógico.

El resultado se almacena en `self.columnas_detectadas` (dict con las 5 listas) y se imprime un resumen al cargar.

### 3. Firma de cada `caso*.py`

Todos los casos reciben un parámetro adicional:

```python
def aplicar_casoN(df, porcentaje_contaminacion, reporte_problemas, columnas_detectadas)
```

`columnas_detectadas` es el dict con las 5 listas. Los casos usan solo los grupos que les aplican.

Si un caso no encuentra columnas aplicables (lista vacía), imprime un aviso y registra `total_problemas: 0` en el reporte, sin lanzar excepción.

### 4. Actualización de call sites en `contaminar_dataset.py`

El método `contaminar_dataset()` actualiza todas las llamadas para pasar `self.columnas_detectadas`:

```python
aplicar_caso1(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
```

`casos/__init__.py` no necesita cambios ya que solo re-exporta los nombres de función.

### 5. Compatibilidad con uso como módulo

`columnas_detectadas` es un parámetro requerido. `ejemplo_uso.py` usa la clase directamente (no llama a funciones de caso individualmente), por lo que sigue funcionando sin cambios siempre que `cargar_dataset()` se llame antes de `contaminar_dataset()` (que es el flujo actual). La API pública de la clase no cambia.

---

## Cambios por caso

### Caso 1 — Normalización de Categorías

- **Columnas:** `cols_categoricas`
- **Lógica:** Para cada columna, obtiene sus valores únicos y genera variaciones automáticas aplicando en este orden de prioridad:
  1. UPPER
  2. lower
  3. Title Case
  4. Espacio al inicio
  5. Espacio al final
  6. Espacios en ambos lados (solo se incluye si el valor ya no cubre los 5 anteriores)
  7. Versión con espacio alrededor del guión (solo si el valor contiene `-`)
- **Cap de variaciones:** Se toman las primeras 5 de la lista anterior. Si el valor no tiene guión, el pool tiene 5 variaciones exactas (1-5). Si tiene guión, el pool tiene 6 y se toman las primeras 5 (se omite la de espacios en ambos lados).
- **Si no hay columnas:** Reporta aviso, `total_problemas: 0`.

### Caso 2 — Validación de Rangos Numéricos

- **Columnas:** `cols_horas` y `cols_numericas`. Las `cols_binarias` se excluyen completamente (no se contaminan ni se mencionan en el reporte de este caso).
- **Reglas de rango** (match case-insensitive sobre nombre de columna):
  - Nombre contiene "hour", "hora" o "time" → rango válido 0-24; valores contaminados: `-5`, `25`, `30`, `48`
  - Nombre contiene "age" o "edad" → rango válido 10-100; valores contaminados: `0`, `5`, `150`, `200`
  - Resto de `cols_numericas` → introduce valores negativos (`-valor_max * 0.5`) o extremadamente altos (`valor_max * 10`), calculados a partir del máximo observado en la columna
- **Si no hay columnas aplicables:** Reporta aviso, `total_problemas: 0`.

### Caso 3 — Detección de Outliers

- **Columnas:** `cols_numericas` y `cols_horas` (se excluyen `cols_binarias`)
- **Lógica:** Para cada columna aplica `mean ± N·std` con N entre 3.5 y 5 (igual que hoy). El valor contaminado se clampea al rango físicamente posible de la columna (min observado − 50%, max observado + 50%) para que sea un outlier estadístico pero no absurdo.
- **Exclusión de baja varianza:** Se omite con aviso si la columna tiene menos de 5 valores únicos (lo que cubre el caso `std == 0` como subconjunto). Esta es la única condición de exclusión.
- **Si no hay columnas aplicables:** Reporta aviso, `total_problemas: 0`.

### Caso 4 — Consistencia entre Columnas

- **Detección de pares:** Solo se buscan pares de exactamente una columna numérica y una columna categórica (nunca dos numéricas ni dos categóricas). Algoritmo:
  1. Normaliza todos los nombres a lowercase con `_` como separador.
  2. Para cada combinación (col de `cols_numericas`, col de `cols_categoricas`), calcula el prefijo común en tokens separados por `_`.
  3. Si el prefijo común tiene ≥ 2 tokens, el par es candidato (ej. `gad_7_score` / `gad_7_severity` → prefijo `gad_7`).
- **Contaminación:** Para cada par encontrado, cambia el valor de la columna categórica a una categoría que no corresponde al valor numérico, usando la distribución de valores únicos de esa columna categórica.
- **Si no se encuentran pares:** Imprime "Caso 4: no se encontraron pares de columnas relacionadas. Omitiendo." y registra `total_problemas: 0`. **No lanza excepción.**

### Caso 5 — Valores Faltantes

- **Columnas:** Todas las columnas excepto `cols_ids` (para no romper claves de identificación)
- **Lógica:** Igual que hoy, itera columnas objetivo e introduce `''`, `'N/A'`, `'NULL'`, `'NaN'`, `'null'`, `'na'`, `'?'`, `'-'`.
- **Si no hay columnas:** Reporta aviso, `total_problemas: 0`.

### Caso 6 — Tipos de Datos (Números como Texto)

- **Columnas:** `cols_numericas` y `cols_horas` (se excluyen `cols_binarias`)
- **Lógica:** Para cualquier columna numérica, sustituye el valor por texto genérico aleatorio de un pool fijo: `['veinte', 'cinco punto tres', 'dieciocho', 'ocho horas', 'twenty', 'five point two', 'N/D', 'n/a', 'treinta y dos', 'doce']`. No se requiere mapeo por columna.
- **Si no hay columnas:** Reporta aviso, `total_problemas: 0`.

### Caso 7 — Limpieza de Formato

- **Columnas:** `cols_ids` + `cols_categoricas`
- **Lógica:** Igual que hoy (espacios al inicio/final, tabs, caracteres especiales `*[]`). Itera sobre todas las columnas de los dos grupos.
- **Si no hay columnas:** Reporta aviso, `total_problemas: 0`.

---

## Archivos a modificar

| Archivo | Tipo de cambio |
|---------|---------------|
| `contaminar_dataset.py` | Agregar `_detectar_columnas()`, actualizar `contaminar_dataset()` para pasar `self.columnas_detectadas` a cada caso, reemplazar `main()` con CLI argparse |
| `casos/caso1.py` | Generar variaciones automáticas desde valores únicos (cap 5 por valor) |
| `casos/caso2.py` | Detectar rangos por nombre de columna (case-insensitive), excluir binarias |
| `casos/caso3.py` | Iterar sobre `cols_numericas` + `cols_horas`, excluir baja varianza y binarias |
| `casos/caso4.py` | Detección de pares por prefijo común (≥2 tokens); omitir si no hay |
| `casos/caso5.py` | Iterar sobre todas las columnas excepto IDs |
| `casos/caso6.py` | Pool de texto genérico para cualquier numérica (excluir binarias) |
| `casos/caso7.py` | Usar `cols_ids` + `cols_categoricas` detectadas |

No se crean archivos nuevos. `casos/__init__.py` y `ejemplo_uso.py` no se modifican.

---

## Criterios de éxito

1. `python contaminar_dataset.py social_media_mental_health.csv` ejecuta los 7 casos sin excepción y el reporte JSON contiene `total_problemas > 0` para los casos 1, 2, 3, 5, 6 y 7 (el caso 4 puede reportar 0 si no detecta pares).
2. `python contaminar_dataset.py Smartphone_Usage_And_Addiction_Analysis_7500_Rows.csv` ejecuta sin excepción y el reporte JSON contiene `total_problemas > 0` para los casos 1, 2, 3, 5, 6 y 7. El caso 4 puede reportar 0 al no tener pares numérico-categórico con prefijo común.
3. El reporte JSON indica explícitamente qué columnas fueron afectadas en cada caso.
4. Si un caso no encuentra columnas aplicables, imprime un aviso descriptivo y continúa sin lanzar excepción.
5. `python contaminar_dataset.py dataset.csv --casos 1 3 5` aplica únicamente los casos 1, 3 y 5.
