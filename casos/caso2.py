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
KEYWORDS_EDAD  = ['age', 'edad']

VALORES_FUERA_HORAS = [-5.0, 25.0, 30.5, 48.0]
VALORES_FUERA_EDAD  = [0, 5, 150, 200]


def _valores_fuera_rango(df: pd.DataFrame, columna: str) -> list:
    col_lower = columna.lower()
    if any(kw in col_lower for kw in KEYWORDS_HORAS):
        return VALORES_FUERA_HORAS
    if any(kw in col_lower for kw in KEYWORDS_EDAD):
        return VALORES_FUERA_EDAD
    val_max = df[columna].max()
    return [-abs(val_max) * 0.5, val_max * 10]


def aplicar_caso2(df: pd.DataFrame, porcentaje_contaminacion: float,
                  reporte_problemas: Dict, columnas_detectadas: Dict) -> None:
    """Introduce valores fuera de rango en columnas numéricas y de horas."""
    print("\n=== CASO 2: Validación de Rangos Numéricos ===")
    problemas_introducidos = []

    cols = (
        columnas_detectadas.get('cols_horas', []) +
        columnas_detectadas.get('cols_numericas', [])
    )

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
        # Asegurar que la columna acepta flotantes (los valores fuera de rango pueden serlo)
        if df[columna].dtype != 'object':
            df[columna] = df[columna].astype(float)
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
