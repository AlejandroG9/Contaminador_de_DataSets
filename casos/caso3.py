"""
CASO 3: Detección de Outliers
Introduce outliers estadísticamente extremos (pero técnicamente posibles)
en todas las columnas numéricas y de horas detectadas.
Excluye columnas con menos de 5 valores únicos.
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
    por_columna = max(1, num_contaminar // len(cols))

    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        col_min = df[col].min()
        col_max = df[col].max()
        rango = col_max - col_min

        # Asegurar que la columna acepta flotantes
        if df[col].dtype != 'object':
            df[col] = df[col].astype(float)
        indices = random.sample(range(num_registros), min(por_columna, num_registros))
        for idx in indices:
            n_sigmas = random.uniform(3.5, 5)
            direccion = 1 if random.random() > 0.5 else -1
            valor_contaminado = mean + direccion * n_sigmas * std
            # Clampear a ±50% del rango observado
            valor_contaminado = max(col_min - rango * 0.5,
                                    min(col_max + rango * 0.5, valor_contaminado))
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
