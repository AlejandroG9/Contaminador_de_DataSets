"""
CASO 4: Validación de Consistencia entre Columnas
Detecta pares (col_numerica, col_categorica) con prefijo común de ≥2 tokens
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

        por_par = max(1, num_contaminar // len(pares))
        indices = random.sample(range(num_registros), min(por_par, num_registros))
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
