# Contaminador Genérico Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactorizar el contaminador de datos para que funcione con cualquier CSV via CLI, usando detección automática de columnas por tipo en lugar de nombres hardcodeados.

**Architecture:** Se agrega `_detectar_columnas()` a `ContaminadorDataset` que clasifica columnas en 5 grupos (ids, categoricas, binarias, horas, numericas). Cada `caso*.py` recibe este dict y opera sobre los grupos relevantes. Se expone un CLI con `argparse`.

**Tech Stack:** Python 3, pandas, numpy, argparse. Tests con pytest.

---

## Archivos involucrados

| Archivo | Acción |
|---------|--------|
| `tests/test_contaminador.py` | Crear — tests de detección de columnas, CLI y casos |
| `contaminar_dataset.py` | Modificar — `_detectar_columnas()`, actualizar `contaminar_dataset()`, reemplazar `main()` con CLI |
| `casos/caso1.py` | Modificar — variaciones automáticas desde valores únicos |
| `casos/caso2.py` | Modificar — rangos por nombre de columna, excluir binarias |
| `casos/caso3.py` | Modificar — iterar cols_numericas + cols_horas, excluir baja cardinalidad |
| `casos/caso4.py` | Modificar — detección de pares por prefijo, omitir si no hay |
| `casos/caso5.py` | Modificar — iterar todas las columnas excepto IDs |
| `casos/caso6.py` | Modificar — pool de texto genérico para numéricas |
| `casos/caso7.py` | Modificar — usar cols_ids + cols_categoricas detectadas |
| `README.md` | Modificar — documentar uso CLI y ejemplos |

---

## Task 1: Setup de tests y detección de columnas

**Files:**
- Create: `tests/test_contaminador.py`
- Modify: `contaminar_dataset.py`

- [ ] **Step 1: Instalar pytest si no está disponible**

```bash
pip install pytest --quiet
```

- [ ] **Step 2: Crear tests para `_detectar_columnas()`**

Crear `tests/test_contaminador.py`:

```python
import pandas as pd
import numpy as np
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contaminar_dataset import ContaminadorDataset


@pytest.fixture
def df_mixto(tmp_path):
    """Dataset de prueba con todos los tipos de columnas."""
    csv = tmp_path / "test.csv"
    df = pd.DataFrame({
        'transaction_id': [f'TXN{i:05d}' for i in range(100)],  # ID (>80% únicos)
        'gender': ['Male', 'Female'] * 50,                        # categórica
        'stress_level': ['Low', 'Medium', 'High', 'Low', 'High'] * 20,  # categórica
        'age': range(18, 118),                                    # numérica
        'sleep_hours': [7.5] * 100,                               # horas (nombre contiene "hours")
        'score': range(0, 100),                                   # numérica
        'addicted_label': [0, 1] * 50,                            # binaria (solo 0 y 1)
    })
    df.to_csv(csv, index=False)
    return str(csv)


def test_detectar_ids(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    assert 'transaction_id' in c.columnas_detectadas['cols_ids']


def test_detectar_categoricas(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    cats = c.columnas_detectadas['cols_categoricas']
    assert 'gender' in cats
    assert 'stress_level' in cats
    assert 'transaction_id' not in cats  # IDs no son categóricas


def test_detectar_binarias(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    assert 'addicted_label' in c.columnas_detectadas['cols_binarias']
    assert 'addicted_label' not in c.columnas_detectadas['cols_numericas']


def test_detectar_horas(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    assert 'sleep_hours' in c.columnas_detectadas['cols_horas']
    assert 'sleep_hours' not in c.columnas_detectadas['cols_numericas']


def test_detectar_numericas(df_mixto, tmp_path):
    c = ContaminadorDataset(df_mixto, str(tmp_path / "out.csv"))
    c.cargar_dataset()
    nums = c.columnas_detectadas['cols_numericas']
    assert 'age' in nums
    assert 'score' in nums
    # binarias y horas no deben estar
    assert 'addicted_label' not in nums
    assert 'sleep_hours' not in nums
```

- [ ] **Step 3: Ejecutar tests — deben fallar**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v 2>&1 | head -30
```

Esperado: `AttributeError: 'ContaminadorDataset' object has no attribute 'columnas_detectadas'`

- [ ] **Step 4: Implementar `_detectar_columnas()` en `contaminar_dataset.py`**

Agregar como método de `ContaminadorDataset`, llamarlo al final de `cargar_dataset()`:

```python
def _detectar_columnas(self):
    """Clasifica las columnas del dataset en 5 grupos por tipo."""
    cols_ids = []
    cols_categoricas = []
    cols_binarias = []
    cols_horas = []
    cols_numericas = []

    n = len(self.df)
    keywords_horas = ['hour', 'hora', 'time']

    for col in self.df.columns:
        col_lower = col.lower()
        dtype = self.df[col].dtype

        if dtype == 'object':
            unique_ratio = self.df[col].nunique() / n
            if unique_ratio > 0.8:
                cols_ids.append(col)
            else:
                cols_categoricas.append(col)
        elif np.issubdtype(dtype, np.number):
            unique_vals = set(self.df[col].dropna().unique())
            if unique_vals <= {0, 1}:
                cols_binarias.append(col)
            elif any(kw in col_lower for kw in keywords_horas):
                cols_horas.append(col)
            else:
                cols_numericas.append(col)

    self.columnas_detectadas = {
        'cols_ids': cols_ids,
        'cols_categoricas': cols_categoricas,
        'cols_binarias': cols_binarias,
        'cols_horas': cols_horas,
        'cols_numericas': cols_numericas,
    }

    print(f"\nColumnas detectadas:")
    for grupo, cols in self.columnas_detectadas.items():
        if cols:
            print(f"  {grupo}: {cols}")
```

Modificar `cargar_dataset()` para llamar `_detectar_columnas()` al final:

```python
def cargar_dataset(self):
    """Carga el dataset original desde el archivo CSV."""
    self.df = pd.read_csv(self.archivo_entrada, encoding=self.encoding)
    print(f"Dataset cargado: {len(self.df)} registros, {len(self.df.columns)} columnas")
    self._detectar_columnas()
```

También agregar `encoding` como parámetro del constructor (default `'utf-8'`):

```python
def __init__(self, archivo_entrada, archivo_salida, porcentaje_contaminacion=0.10, encoding='utf-8'):
    ...
    self.encoding = encoding
    self.columnas_detectadas = {}
```

- [ ] **Step 5: Ejecutar tests — deben pasar**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v
```

Esperado: 5 tests PASSED

- [ ] **Step 6: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add tests/test_contaminador.py contaminar_dataset.py && git commit -m "feat: agregar detección automática de columnas por tipo"
```

---

## Task 2: Actualizar firma de casos y llamadas en contaminar_dataset.py

**Files:**
- Modify: `contaminar_dataset.py`

- [ ] **Step 1: Actualizar `contaminar_dataset()` para pasar `columnas_detectadas` a cada caso**

Reemplazar cada llamada de la forma:
```python
aplicar_caso1(self.df, self.porcentaje_contaminacion, self.reporte_problemas)
```
por:
```python
aplicar_caso1(self.df, self.porcentaje_contaminacion, self.reporte_problemas, self.columnas_detectadas)
```
Para los 7 casos.

- [ ] **Step 2: Verificar que el script aún corre (los casos fallarán por firma incorrecta hasta Task 3-9)**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -c "from contaminar_dataset import ContaminadorDataset; print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add contaminar_dataset.py && git commit -m "feat: pasar columnas_detectadas a todos los casos"
```

---

## Task 3: Refactorizar caso1.py

**Files:**
- Modify: `casos/caso1.py`

- [ ] **Step 1: Agregar test para caso1 genérico**

En `tests/test_contaminador.py`:

```python
def test_caso1_contamina_categoricas(df_mixto, tmp_path):
    from casos.caso1 import aplicar_caso1
    import pandas as pd
    df = pd.read_csv(df_mixto)
    reporte = {}
    cols_detectadas = {
        'cols_ids': ['transaction_id'],
        'cols_categoricas': ['gender', 'stress_level'],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso1(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso1_normalizacion_categorias']['total_problemas'] > 0


def test_caso1_sin_categoricas(tmp_path):
    from casos.caso1 import aplicar_caso1
    import pandas as pd
    df = pd.DataFrame({'age': range(100), 'score': range(100)})
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': [], 'cols_binarias': [],
        'cols_horas': [], 'cols_numericas': ['age', 'score'],
    }
    aplicar_caso1(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso1_normalizacion_categorias']['total_problemas'] == 0
```

- [ ] **Step 2: Reemplazar `casos/caso1.py` completo**

```python
"""
CASO 1: Normalización de Categorías
Introduce variaciones de formato en columnas categóricas detectadas automáticamente:
- Variaciones de mayúsculas/minúsculas
- Espacios extra al inicio/final
- Variaciones en guiones
"""

import random
import pandas as pd
from typing import Dict


def _generar_variaciones(valor: str) -> list:
    """Genera hasta 5 variaciones de formato para un valor de texto."""
    candidatos = [
        valor.upper(),
        valor.lower(),
        valor.title(),
        f" {valor}",
        f"{valor} ",
        f" {valor} ",
    ]
    if '-' in valor:
        candidatos.append(valor.replace('-', ' - '))
    # Eliminar duplicados preservando orden, tomar primeros 5
    vistos = set()
    resultado = []
    for v in candidatos:
        if v not in vistos and v != valor:
            vistos.add(v)
            resultado.append(v)
        if len(resultado) == 5:
            break
    return resultado


def aplicar_caso1(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """
    Introduce problemas de normalización en columnas categóricas detectadas.
    """
    print("\n=== CASO 1: Normalización de Categorías ===")
    problemas_introducidos = []

    cols = columnas_detectadas.get('cols_categoricas', [])
    if not cols:
        print("  ⚠ No se encontraron columnas categóricas. Omitiendo caso 1.")
        reporte_problemas['caso1_normalizacion_categorias'] = {
            'descripcion': 'No se encontraron columnas categóricas',
            'total_problemas': 0, 'problemas': []
        }
        return

    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)

    for columna in cols:
        valores_unicos = df[columna].dropna().unique().tolist()
        if not valores_unicos:
            continue

        # Construir pool de variaciones para todos los valores únicos
        pool_variaciones = []
        for val in valores_unicos:
            pool_variaciones.extend(_generar_variaciones(str(val)))

        if not pool_variaciones:
            continue

        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_contaminado = random.choice(pool_variaciones)
            df.at[idx, columna] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado
            })

    reporte_problemas['caso1_normalizacion_categorias'] = {
        'descripcion': 'Problemas de normalización en categorías (mayúsculas, espacios, guiones)',
        'columnas_afectadas': cols,
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} problemas de normalización en: {cols}")
```

- [ ] **Step 3: Ejecutar tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v -k "caso1"
```

Esperado: 2 tests PASSED

- [ ] **Step 4: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add casos/caso1.py tests/test_contaminador.py && git commit -m "feat: caso1 genérico con variaciones automáticas"
```

---

## Task 4: Refactorizar caso2.py

**Files:**
- Modify: `casos/caso2.py`

- [ ] **Step 1: Agregar test para caso2 genérico**

En `tests/test_contaminador.py`:

```python
def test_caso2_contamina_horas_y_numericas(tmp_path):
    from casos.caso2 import aplicar_caso2
    import pandas as pd
    df = pd.DataFrame({
        'age': [20] * 100,
        'sleep_hours': [7.5] * 100,
        'score': [50] * 100,
        'addicted_label': [0, 1] * 50,
    })
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': [],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['age', 'score'],
    }
    aplicar_caso2(df, 0.20, reporte, cols_detectadas)
    assert reporte['caso2_validacion_rangos']['total_problemas'] > 0
    # binarias no deben contaminarse
    assert df['addicted_label'].isin([0, 1]).all()
```

- [ ] **Step 2: Reemplazar `casos/caso2.py` completo**

```python
"""
CASO 2: Validación de Rangos Numéricos
Introduce valores fuera de rango en columnas numéricas detectadas automáticamente.
Reglas por nombre de columna (case-insensitive):
- "hour"/"hora"/"time" → rango 0-24
- "age"/"edad"         → rango 10-100
- resto                → negativo o 10× el máximo observado
Las columnas binarias (0/1) se excluyen completamente.
"""

import random
import pandas as pd
from typing import Dict

KEYWORDS_HORAS = ['hour', 'hora', 'time']
KEYWORDS_EDAD = ['age', 'edad']

VALORES_FUERA_HORAS = [-5.0, 25.0, 30.5, 48.0]
VALORES_FUERA_EDAD = [0, 5, 150, 200]


def _valores_fuera_rango(df: pd.DataFrame, columna: str) -> list:
    col_lower = columna.lower()
    if any(kw in col_lower for kw in KEYWORDS_HORAS):
        return VALORES_FUERA_HORAS
    if any(kw in col_lower for kw in KEYWORDS_EDAD):
        return VALORES_FUERA_EDAD
    # Fallback: negativo o 10× el máximo
    val_max = df[columna].max()
    return [-abs(val_max) * 0.5, val_max * 10]


def aplicar_caso2(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce valores fuera de rango en columnas numéricas y de horas."""
    print("\n=== CASO 2: Validación de Rangos Numéricos ===")
    problemas_introducidos = []

    cols = columnas_detectadas.get('cols_horas', []) + columnas_detectadas.get('cols_numericas', [])
    # Excluir binarias
    cols_binarias = columnas_detectadas.get('cols_binarias', [])
    cols = [c for c in cols if c not in cols_binarias]

    if not cols:
        print("  ⚠ No se encontraron columnas numéricas aplicables. Omitiendo caso 2.")
        reporte_problemas['caso2_validacion_rangos'] = {
            'descripcion': 'No se encontraron columnas numéricas aplicables',
            'total_problemas': 0, 'problemas': []
        }
        return

    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)

    for columna in cols:
        valores_fuera = _valores_fuera_rango(df, columna)
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_contaminado = random.choice(valores_fuera)
            df.at[idx, columna] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado,
                'problema': f'Valor fuera de rango en {columna}'
            })

    reporte_problemas['caso2_validacion_rangos'] = {
        'descripcion': 'Valores numéricos fuera de rangos válidos o lógicos',
        'columnas_afectadas': cols,
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} valores fuera de rango en: {cols}")
```

- [ ] **Step 3: Ejecutar tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v -k "caso2"
```

Esperado: 1 test PASSED

- [ ] **Step 4: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add casos/caso2.py tests/test_contaminador.py && git commit -m "feat: caso2 genérico con rangos por nombre de columna"
```

---

## Task 5: Refactorizar caso3.py

**Files:**
- Modify: `casos/caso3.py`

- [ ] **Step 1: Agregar test para caso3 genérico**

En `tests/test_contaminador.py`:

```python
def test_caso3_outliers_columnas_numericas(tmp_path):
    from casos.caso3 import aplicar_caso3
    import pandas as pd, numpy as np
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        'score': rng.integers(0, 100, 200).astype(float),
        'sleep_hours': rng.uniform(4, 10, 200),
        'addicted_label': [0, 1] * 100,
    })
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': [],
        'cols_binarias': ['addicted_label'],
        'cols_horas': ['sleep_hours'],
        'cols_numericas': ['score'],
    }
    aplicar_caso3(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso3_outliers']['total_problemas'] > 0
    assert df['addicted_label'].isin([0, 1]).all()
```

- [ ] **Step 2: Reemplazar `casos/caso3.py` completo**

```python
"""
CASO 3: Detección de Outliers
Introduce outliers estadísticamente extremos (pero técnicamente posibles)
en todas las columnas numéricas y de horas detectadas.
Excluye columnas binarias y columnas con menos de 5 valores únicos.
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso3(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce outliers estadísticos en columnas numéricas y de horas."""
    print("\n=== CASO 3: Detección de Outliers ===")
    problemas_introducidos = []

    cols_candidatas = (
        columnas_detectadas.get('cols_numericas', []) +
        columnas_detectadas.get('cols_horas', [])
    )

    cols = []
    for col in cols_candidatas:
        if df[col].nunique() < 5:
            print(f"  ⚠ Columna '{col}' tiene <5 valores únicos, se omite.")
            continue
        cols.append(col)

    if not cols:
        print("  ⚠ No se encontraron columnas numéricas aplicables. Omitiendo caso 3.")
        reporte_problemas['caso3_outliers'] = {
            'descripcion': 'No se encontraron columnas numéricas con suficiente varianza',
            'total_problemas': 0, 'problemas': []
        }
        return

    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)

    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        col_min = df[col].min()
        col_max = df[col].max()
        rango = col_max - col_min

        indices = random.sample(range(num_registros), min(num_contaminar // max(len(cols), 1), num_registros))
        for idx in indices:
            n_sigmas = random.uniform(3.5, 5)
            direccion = 1 if random.random() > 0.5 else -1
            valor_contaminado = mean + direccion * n_sigmas * std
            # Clampear a ±50% del rango observado para evitar valores absurdos
            valor_contaminado = max(col_min - rango * 0.5, min(col_max + rango * 0.5, valor_contaminado))
            valor_original = df.at[idx, col]
            df.at[idx, col] = round(valor_contaminado, 2)
            problemas_introducidos.append({
                'indice': idx,
                'columna': col,
                'valor_original': round(float(valor_original), 2),
                'valor_contaminado': round(valor_contaminado, 2),
                'problema': 'Outlier estadístico'
            })

    reporte_problemas['caso3_outliers'] = {
        'descripcion': 'Outliers estadísticamente extremos pero técnicamente posibles',
        'columnas_afectadas': cols,
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} outliers en: {cols}")
```

- [ ] **Step 3: Ejecutar tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v -k "caso3"
```

Esperado: 1 test PASSED

- [ ] **Step 4: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add casos/caso3.py tests/test_contaminador.py && git commit -m "feat: caso3 genérico con outliers en cualquier columna numérica"
```

---

## Task 6: Refactorizar caso4.py

**Files:**
- Modify: `casos/caso4.py`

- [ ] **Step 1: Agregar test para caso4 genérico**

En `tests/test_contaminador.py`:

```python
def test_caso4_detecta_pares_por_prefijo(tmp_path):
    from casos.caso4 import aplicar_caso4, _detectar_pares
    pares = _detectar_pares(
        ['gad_7_score', 'phq_9_score'],
        ['gad_7_severity', 'phq_9_severity', 'gender']
    )
    assert ('gad_7_score', 'gad_7_severity') in pares
    assert ('phq_9_score', 'phq_9_severity') in pares
    assert len(pares) == 2


def test_caso4_sin_pares_no_falla(tmp_path):
    from casos.caso4 import aplicar_caso4
    import pandas as pd
    df = pd.DataFrame({'score': range(100), 'gender': ['M', 'F'] * 50})
    reporte = {}
    cols_detectadas = {
        'cols_ids': [], 'cols_categoricas': ['gender'],
        'cols_binarias': [], 'cols_horas': [], 'cols_numericas': ['score'],
    }
    aplicar_caso4(df, 0.10, reporte, cols_detectadas)
    assert reporte['caso4_consistencia']['total_problemas'] == 0
```

- [ ] **Step 2: Reemplazar `casos/caso4.py` completo**

```python
"""
CASO 4: Validación de Consistencia entre Columnas
Detecta pares (col_numerica, col_categorica) con prefijo común (≥2 tokens)
e introduce inconsistencias entre ellos.
Si no hay pares, omite el caso sin error.
"""

import random
import pandas as pd
from typing import Dict, List, Tuple


def _prefijo_comun(nombre_a: str, nombre_b: str) -> List[str]:
    """Retorna los tokens del prefijo común entre dos nombres de columna."""
    tokens_a = nombre_a.lower().split('_')
    tokens_b = nombre_b.lower().split('_')
    prefijo = []
    for ta, tb in zip(tokens_a, tokens_b):
        if ta == tb:
            prefijo.append(ta)
        else:
            break
    return prefijo


def _detectar_pares(cols_numericas: List[str], cols_categoricas: List[str]) -> List[Tuple[str, str]]:
    """Detecta pares (numérica, categórica) con prefijo común de ≥2 tokens."""
    pares = []
    for num in cols_numericas:
        for cat in cols_categoricas:
            if len(_prefijo_comun(num, cat)) >= 2:
                pares.append((num, cat))
    return pares


def aplicar_caso4(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce inconsistencias entre pares de columnas relacionadas detectadas."""
    print("\n=== CASO 4: Validación de Consistencia entre Columnas ===")

    pares = _detectar_pares(
        columnas_detectadas.get('cols_numericas', []),
        columnas_detectadas.get('cols_categoricas', [])
    )

    if not pares:
        print("  ⚠ Caso 4: no se encontraron pares de columnas relacionadas. Omitiendo.")
        reporte_problemas['caso4_consistencia'] = {
            'descripcion': 'No se encontraron pares de columnas relacionadas',
            'total_problemas': 0, 'problemas': []
        }
        return

    problemas_introducidos = []
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)

    for col_num, col_cat in pares:
        categorias = df[col_cat].dropna().unique().tolist()
        if len(categorias) < 2:
            continue

        indices = random.sample(range(num_registros), min(num_contaminar // max(len(pares), 1), num_registros))
        for idx in indices:
            valor_cat_original = df.at[idx, col_cat]
            otras_categorias = [c for c in categorias if c != valor_cat_original]
            if not otras_categorias:
                continue
            valor_contaminado = random.choice(otras_categorias)
            df.at[idx, col_cat] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'col_numerica': col_num,
                'col_categorica': col_cat,
                'valor_original': valor_cat_original,
                'valor_contaminado': valor_contaminado,
                'problema': f'Inconsistencia entre {col_num} y {col_cat}'
            })

    reporte_problemas['caso4_consistencia'] = {
        'descripcion': 'Inconsistencias entre columnas relacionadas (pares por prefijo común)',
        'pares_detectados': [f"{n} / {c}" for n, c in pares],
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidas {len(problemas_introducidos)} inconsistencias en pares: {pares}")
```

- [ ] **Step 3: Ejecutar tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v -k "caso4"
```

Esperado: 2 tests PASSED

- [ ] **Step 4: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add casos/caso4.py tests/test_contaminador.py && git commit -m "feat: caso4 con detección automática de pares por prefijo"
```

---

## Task 7: Refactorizar caso5.py, caso6.py, caso7.py

**Files:**
- Modify: `casos/caso5.py`, `casos/caso6.py`, `casos/caso7.py`

- [ ] **Step 1: Reemplazar `casos/caso5.py`**

```python
"""
CASO 5: Manejo de Valores Faltantes
Introduce valores faltantes en todas las columnas excepto IDs.
"""

import random
import pandas as pd
from typing import Dict

VALORES_FALTANTES = ['', 'N/A', 'NULL', 'NaN', 'null', 'na', '?', '-']


def aplicar_caso5(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce valores faltantes en todas las columnas excepto IDs."""
    print("\n=== CASO 5: Manejo de Valores Faltantes ===")
    problemas_introducidos = []

    cols_ids = columnas_detectadas.get('cols_ids', [])
    cols = [c for c in df.columns if c not in cols_ids]

    if not cols:
        print("  ⚠ No se encontraron columnas aplicables. Omitiendo caso 5.")
        reporte_problemas['caso5_valores_faltantes'] = {
            'descripcion': 'No se encontraron columnas aplicables',
            'total_problemas': 0, 'problemas': []
        }
        return

    num_registros = len(df)
    num_contaminar = max(1, int(num_registros * porcentaje_contaminacion) // len(cols))

    for columna in cols:
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_faltante = random.choice(VALORES_FALTANTES)
            df.at[idx, columna] = valor_faltante
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_faltante': valor_faltante,
                'problema': f'Valor faltante representado como: {repr(valor_faltante)}'
            })

    reporte_problemas['caso5_valores_faltantes'] = {
        'descripcion': 'Valores faltantes (vacíos, N/A, NULL, etc.)',
        'columnas_afectadas': cols,
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} valores faltantes en {len(cols)} columnas")
```

- [ ] **Step 2: Reemplazar `casos/caso6.py`**

```python
"""
CASO 6: Normalización de Tipos de Datos
Introduce texto en columnas que deberían ser numéricas.
Usa un pool genérico de palabras. Excluye columnas binarias.
"""

import random
import pandas as pd
from typing import Dict

POOL_TEXTO = [
    'veinte', 'cinco punto tres', 'dieciocho', 'ocho horas', 'treinta y dos',
    'twenty', 'five point two', 'twelve', 'seven', 'N/D', 'n/a', 'doce', 'nueve',
]


def aplicar_caso6(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce texto en columnas numéricas y de horas (excluye binarias)."""
    print("\n=== CASO 6: Normalización de Tipos de Datos ===")
    problemas_introducidos = []

    cols = (
        columnas_detectadas.get('cols_numericas', []) +
        columnas_detectadas.get('cols_horas', [])
    )

    if not cols:
        print("  ⚠ No se encontraron columnas numéricas aplicables. Omitiendo caso 6.")
        reporte_problemas['caso6_tipos_datos'] = {
            'descripcion': 'No se encontraron columnas numéricas aplicables',
            'total_problemas': 0, 'problemas': []
        }
        return

    num_registros = len(df)
    num_contaminar = max(1, int(num_registros * porcentaje_contaminacion) // len(cols))

    for columna in cols:
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_texto = random.choice(POOL_TEXTO)
            df.at[idx, columna] = valor_texto
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_texto': valor_texto,
                'problema': f'Valor numérico como texto: {valor_texto}'
            })

    reporte_problemas['caso6_tipos_datos'] = {
        'descripcion': 'Valores numéricos representados como texto',
        'columnas_afectadas': cols,
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} valores numéricos como texto en: {cols}")
```

- [ ] **Step 3: Reemplazar `casos/caso7.py`**

```python
"""
CASO 7: Limpieza de Formato
Introduce espacios extra y caracteres especiales en columnas de IDs y categóricas.
"""

import random
import pandas as pd
from typing import Dict


def _contaminar_formato(valor: str) -> str:
    """Introduce un problema de formato aleatorio en un string."""
    opciones = [
        f" {valor}",
        f"{valor} ",
        f"  {valor}  ",
        f"{valor}\t",
        f"*{valor}*",
        f"[{valor}]",
        f"\t{valor}\t",
    ]
    return random.choice(opciones)


def aplicar_caso7(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce problemas de formato en IDs y columnas categóricas."""
    print("\n=== CASO 7: Limpieza de Formato ===")
    problemas_introducidos = []

    cols = (
        columnas_detectadas.get('cols_ids', []) +
        columnas_detectadas.get('cols_categoricas', [])
    )

    if not cols:
        print("  ⚠ No se encontraron columnas de texto aplicables. Omitiendo caso 7.")
        reporte_problemas['caso7_formato'] = {
            'descripcion': 'No se encontraron columnas de texto aplicables',
            'total_problemas': 0, 'problemas': []
        }
        return

    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)

    for columna in cols:
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_contaminado = _contaminar_formato(str(valor_original))
            df.at[idx, columna] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_contaminado': repr(valor_contaminado),
                'problema': 'Espacios extra o caracteres especiales'
            })

    reporte_problemas['caso7_formato'] = {
        'descripcion': 'Problemas de formato (espacios extra, caracteres especiales)',
        'columnas_afectadas': cols,
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} problemas de formato en: {cols}")
```

- [ ] **Step 4: Ejecutar todos los tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v
```

Esperado: todos los tests previos siguen en PASSED

- [ ] **Step 5: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add casos/caso5.py casos/caso6.py casos/caso7.py && git commit -m "feat: casos 5, 6 y 7 genéricos"
```

---

## Task 8: Agregar CLI con argparse

**Files:**
- Modify: `contaminar_dataset.py`

- [ ] **Step 1: Agregar test CLI**

En `tests/test_contaminador.py`:

```python
def test_cli_genera_archivos(df_mixto, tmp_path):
    import subprocess, json, os
    salida = str(tmp_path / "out.csv")
    result = subprocess.run(
        ['python', 'contaminar_dataset.py', df_mixto, '--salida', salida, '--porcentaje', '0.10'],
        capture_output=True, text=True,
        cwd='/Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos'
    )
    assert result.returncode == 0, result.stderr
    assert os.path.exists(salida)
    reporte = salida.replace('.csv', '_reporte.json')
    assert os.path.exists(reporte)
    with open(reporte) as f:
        data = json.load(f)
    assert 'caso1_normalizacion_categorias' in data


def test_cli_casos_especificos(df_mixto, tmp_path):
    import subprocess, json, os
    salida = str(tmp_path / "out2.csv")
    result = subprocess.run(
        ['python', 'contaminar_dataset.py', df_mixto, '--salida', salida, '--casos', '1', '5'],
        capture_output=True, text=True,
        cwd='/Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos'
    )
    assert result.returncode == 0, result.stderr
    reporte = salida.replace('.csv', '_reporte.json')
    with open(reporte) as f:
        data = json.load(f)
    assert 'caso1_normalizacion_categorias' in data
    assert 'caso2_validacion_rangos' not in data
```

- [ ] **Step 2: Reemplazar la función `main()` con CLI en `contaminar_dataset.py`**

```python
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Contamina intencionalmente un dataset CSV con 7 tipos de problemas de calidad de datos.'
    )
    parser.add_argument('archivo', help='Ruta al archivo CSV de entrada')
    parser.add_argument('--salida', default=None,
                        help='Ruta del CSV contaminado (default: <nombre>_contaminado.csv)')
    parser.add_argument('--porcentaje', type=float, default=0.10,
                        help='Porcentaje de registros a contaminar por caso (default: 0.10)')
    parser.add_argument('--casos', type=int, nargs='+', default=list(range(1, 8)),
                        choices=range(1, 8), metavar='N',
                        help='Casos a aplicar, p.ej. --casos 1 3 5 (default: todos)')
    parser.add_argument('--encoding', default='utf-8',
                        help='Encoding del CSV (default: utf-8). Usa latin-1 si hay problemas.')

    args = parser.parse_args()

    # Construir ruta de salida
    if args.salida is None:
        base = args.archivo.rsplit('.', 1)[0]
        args.salida = f"{base}_contaminado.csv"

    # Convertir enteros a nombres de caso
    casos_activados = [f'caso{n}' for n in args.casos]

    try:
        contaminador = ContaminadorDataset(
            archivo_entrada=args.archivo,
            archivo_salida=args.salida,
            porcentaje_contaminacion=args.porcentaje,
            encoding=args.encoding,
        )
        contaminador.cargar_dataset()
        contaminador.contaminar_dataset(casos_activados=casos_activados)
        contaminador.guardar_dataset()
        contaminador.generar_reporte()

        print("\n✓ Proceso completado exitosamente!")
        print(f"  - Dataset original:    {args.archivo}")
        print(f"  - Dataset contaminado: {args.salida}")
        print(f"  - Reporte:             {args.salida.replace('.csv', '_reporte.json')}")

    except UnicodeDecodeError:
        print(f"\nError al leer el archivo: encoding incorrecto.")
        print(f"Prueba con --encoding latin-1")
        raise SystemExit(1)
    except FileNotFoundError:
        print(f"\nError: no se encontró el archivo '{args.archivo}'")
        raise SystemExit(1)
```

- [ ] **Step 3: Ejecutar todos los tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v
```

Esperado: todos PASSED

- [ ] **Step 4: Probar con los dos datasets reales**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python contaminar_dataset.py social_media_mental_health.csv --salida social_media_mental_health_contaminado.csv
```

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python contaminar_dataset.py "Smartphone_Usage_And_Addiction_Analysis_7500_Rows.csv"
```

Esperado: ambos corren sin errores, generan CSV y JSON de reporte.

- [ ] **Step 5: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add contaminar_dataset.py tests/test_contaminador.py && git commit -m "feat: agregar CLI con argparse"
```

---

## Task 9: Actualizar README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Actualizar README con sección de uso CLI**

Agregar sección completa de uso al README con:
- Descripción del proyecto
- Requisitos
- Instalación
- Uso básico (CLI)
- Uso avanzado (casos específicos, porcentaje, encoding)
- Los 7 casos documentados
- Uso como módulo Python

- [ ] **Step 2: Commit**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && git add README.md && git commit -m "docs: documentar uso CLI y los 7 casos en README"
```

---

## Verificación final

- [ ] **Ejecutar suite completa de tests**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -m pytest tests/test_contaminador.py -v
```

- [ ] **Verificar que ambos datasets producen reportes con `total_problemas > 0` en los casos 1, 2, 3, 5, 6, 7**

```bash
cd /Users/alejandrogonzalezturrubiates/Proyectos/Contaminador_de_Datos && python -c "
import json
for f in ['social_media_mental_health_contaminado_reporte.json', 'Smartphone_Usage_And_Addiction_Analysis_7500_Rows_contaminado_reporte.json']:
    try:
        with open(f) as fp:
            data = json.load(fp)
        print(f)
        for k, v in data.items():
            print(f'  {k}: {v[\"total_problemas\"]} problemas')
    except FileNotFoundError:
        print(f'{f} no encontrado')
"
```
