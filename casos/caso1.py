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
    # Eliminar duplicados y el valor original, tomar primeros 5
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
    """Introduce problemas de normalización en columnas categóricas detectadas."""
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
