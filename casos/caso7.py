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
