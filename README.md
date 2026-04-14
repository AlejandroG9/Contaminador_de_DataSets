# Contaminador de Datos

Herramienta educativa para la materia de **Ingeniería de la Información**. Introduce intencionalmente 7 tipos de problemas de calidad de datos en cualquier CSV, para que los alumnos los identifiquen y corrijan.

---

## Requisitos

```bash
pip install pandas numpy
```

---

## Uso por línea de comandos (CLI)

### Uso mínimo

```bash
python3 contaminar_dataset.py mi_dataset.csv
```

Genera automáticamente:
- `mi_dataset_contaminado.csv` — dataset con problemas introducidos
- `mi_dataset_contaminado_reporte.json` — detalle de cada problema

### Opciones disponibles

```bash
python3 contaminar_dataset.py mi_dataset.csv [opciones]
```

| Opción | Descripción | Default |
|--------|-------------|---------|
| `--salida archivo.csv` | Ruta del archivo de salida | `<nombre>_contaminado.csv` |
| `--porcentaje 0.15` | Fracción de registros a contaminar por caso | `0.10` (10%) |
| `--casos 1 3 5` | Qué casos aplicar (1 al 7) | Todos |
| `--encoding latin-1` | Encoding del CSV | `utf-8` |

### Ejemplos

```bash
# Contaminar con todos los casos al 10%
python3 contaminar_dataset.py datos_alumnos.csv

# Solo casos 1, 3 y 5 con 15% de contaminación
python3 contaminar_dataset.py ventas.csv --casos 1 3 5 --porcentaje 0.15

# Especificar archivo de salida
python3 contaminar_dataset.py encuesta.csv --salida encuesta_ejercicio.csv

# CSV con encoding especial (archivos de Excel en español)
python3 contaminar_dataset.py reporte.csv --encoding latin-1
```

---

## Detección automática de columnas

El script analiza el dataset al cargarlo y clasifica las columnas automáticamente:

| Grupo | Criterio | Ejemplos |
|-------|----------|---------|
| **IDs** | Texto con >80% valores únicos | `user_id`, `transaction_id` |
| **Categóricas** | Texto con valores repetidos | `gender`, `stress_level` |
| **Binarias** | Numéricas con solo valores 0 y 1 | `addicted_label` |
| **Horas** | Numéricas cuyo nombre contiene "hour/hora/time" | `sleep_hours`, `screen_time` |
| **Numéricas** | Resto de columnas numéricas | `age`, `score` |

No es necesario configurar nada: el script aplica cada caso al grupo de columnas que corresponde.

---

## Los 7 casos de contaminación

### Caso 1 — Normalización de Categorías
Introduce variaciones de mayúsculas, espacios y guiones en columnas categóricas.

| Valor original | Variación introducida |
|---------------|----------------------|
| `Male` | `MALE`, `male`, ` Male`, `Male ` |
| `High` | `HIGH`, `high`, ` High ` |

**Columnas afectadas:** todas las categóricas detectadas.

---

### Caso 2 — Validación de Rangos Numéricos
Introduce valores fuera del rango lógico de cada columna.

| Tipo de columna | Valores fuera de rango |
|-----------------|------------------------|
| Horas (`*hours*`, `*time*`) | `-5`, `25`, `30.5`, `48` |
| Edad (`*age*`, `*edad*`) | `0`, `5`, `150`, `200` |
| Resto de numéricas | Negativos o 10× el máximo |

**Columnas afectadas:** horas y numéricas (excluye binarias).

---

### Caso 3 — Detección de Outliers
Introduce valores estadísticamente extremos (> 3.5 desviaciones estándar) pero dentro del rango físicamente posible.

**Columnas afectadas:** horas y numéricas con al menos 5 valores únicos.

---

### Caso 4 — Consistencia entre Columnas
Detecta automáticamente pares de columnas relacionadas (prefijo común de ≥2 palabras) e introduce inconsistencias entre ellas.

| Ejemplo de par detectado | Inconsistencia |
|--------------------------|---------------|
| `gad_7_score` / `gad_7_severity` | Score alto con severidad baja |
| `phq_9_score` / `phq_9_severity` | Score bajo con severidad alta |

Si no se detectan pares, este caso se omite sin error.

---

### Caso 5 — Valores Faltantes
Introduce representaciones de nulos en todas las columnas (excepto IDs).

Valores usados: `""`, `"N/A"`, `"NULL"`, `"NaN"`, `"null"`, `"na"`, `"?"`, `"-"`

---

### Caso 6 — Tipos de Datos
Reemplaza valores numéricos con su equivalente en texto (español e inglés).

| Valor original | Valor contaminado |
|---------------|------------------|
| `20` | `"veinte"`, `"twenty"` |
| `7.5` | `"cinco punto tres"`, `"N/D"` |

**Columnas afectadas:** horas y numéricas (excluye binarias).

---

### Caso 7 — Limpieza de Formato
Introduce espacios, tabs y caracteres especiales en columnas de texto.

| Valor original | Variación introducida |
|---------------|----------------------|
| `Male` | `" Male"`, `"Male\t"`, `"[Male]"` |
| `U00001` | `" U00001 "`, `"*U00001*"` |

**Columnas afectadas:** IDs y categóricas.

---

## Uso como módulo Python

```python
from contaminar_dataset import ContaminadorDataset

contaminador = ContaminadorDataset(
    archivo_entrada='mi_dataset.csv',
    archivo_salida='mi_dataset_contaminado.csv',
    porcentaje_contaminacion=0.10
)

contaminador.cargar_dataset()
contaminador.contaminar_dataset()              # Todos los casos
# contaminador.contaminar_dataset(casos_activados=['caso1', 'caso3', 'caso5'])
contaminador.guardar_dataset()
contaminador.generar_reporte()
```

---

## Estructura del reporte JSON

```json
{
  "caso1_normalizacion_categorias": {
    "descripcion": "Problemas de normalización en categorías",
    "columnas_afectadas": ["gender", "stress_level"],
    "total_problemas": 3000,
    "problemas": [
      {
        "indice": 42,
        "columna": "gender",
        "valor_original": "Male",
        "valor_contaminado": "MALE"
      }
    ]
  },
  "caso4_consistencia": {
    "descripcion": "Inconsistencias entre columnas relacionadas",
    "pares_detectados": ["gad_7_score / gad_7_severity"],
    "total_problemas": 800,
    "problemas": [...]
  }
}
```

---

## Notas para el docente

- **El dataset original no se modifica** — siempre se crea un nuevo archivo.
- **Reproducibilidad** — se usa `random.seed(42)` para que el resultado sea igual en cada ejecución.
- **El caso 4 es automático** — detecta pares de columnas relacionadas por nombre. Funciona con datasets que tengan columnas como `score`/`severity`, `nivel`/`categoria`, etc.
- **Datasets sin pares relacionados** — el caso 4 reporta 0 problemas y continúa sin error.

---

## Flujo sugerido en clase

1. Mostrar el dataset original (limpio).
2. Ejecutar el script para generar el dataset contaminado.
3. Usar el reporte JSON para mostrar exactamente qué se contaminó en cada caso.
4. Pedir a los alumnos que identifiquen y corrijan cada tipo de problema.
5. Comparar el dataset limpiado con el original usando el reporte.

---

*Script educativo para Ingeniería de la Información.*
