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
        # Convertir a object para poder introducir texto en columnas numéricas
        df[columna] = df[columna].astype(object)
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
