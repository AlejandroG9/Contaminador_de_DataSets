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
        # Convertir a object para poder mezclar tipos (texto en columnas numéricas)
        df[columna] = df[columna].astype(object)
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
