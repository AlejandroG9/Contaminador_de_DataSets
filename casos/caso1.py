"""
CASO 1: Normalización de Categorías
Introduce problemas de normalización en columnas categóricas:
- Variaciones de mayúsculas/minúsculas
- Espacios extra al inicio/final
- Variaciones en guiones y espacios
"""

import random
import pandas as pd
from typing import List, Dict


def aplicar_caso1(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce problemas de normalización en columnas categóricas.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 1: Normalización de Categorías ===")
    problemas_introducidos = []
    
    # Configuración de problemas por columna
    configuracion = {
        'Gender': {
            'variaciones': ['male', 'MALE', 'female', 'FEMALE', ' Male', 'Female ', '  Male  '],
            'descripcion': 'Variaciones de mayúsculas/minúsculas y espacios en Gender'
        },
        'User_Archetype': {
            'variaciones': ['hyper-connected', 'HYPER-CONNECTED', 'Hyper Connected', 'hyper connected', ' Average User'],
            'descripcion': 'Variaciones de formato en User_Archetype'
        },
        'Primary_Platform': {
            'variaciones': ['facebook', 'FACEBOOK', 'twitter', 'Twitter', ' YouTube ', 'instagram'],
            'descripcion': 'Variaciones de mayúsculas y espacios en Primary_Platform'
        },
        'Dominant_Content_Type': {
            'variaciones': ['gaming', 'GAMING', 'Educational-Tech', 'Educational Tech', ' Entertainment/Comedy '],
            'descripcion': 'Variaciones de formato en Dominant_Content_Type'
        },
        'Activity_Type': {
            'variaciones': ['active', 'ACTIVE', ' passive', 'Passive '],
            'descripcion': 'Variaciones de mayúsculas y espacios en Activity_Type'
        },
        'GAD_7_Severity': {
            'variaciones': ['minimal', 'MILD', 'moderate', ' severe', 'Severe '],
            'descripcion': 'Variaciones de mayúsculas y espacios en GAD_7_Severity'
        },
        'PHQ_9_Severity': {
            'variaciones': ['mild', 'MODERATE', 'none-minimal', 'None Minimal', ' Moderately Severe '],
            'descripcion': 'Variaciones de formato en PHQ_9_Severity'
        }
    }
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    
    for columna, config in configuracion.items():
        if columna not in df.columns:
            continue
            
        # Seleccionar registros aleatorios para contaminar
        indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
        
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_contaminado = random.choice(config['variaciones'])
            df.at[idx, columna] = valor_contaminado
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_contaminado': valor_contaminado
            })
    
    reporte_problemas['caso1_normalizacion_categorias'] = {
        'descripcion': 'Problemas de normalización en categorías (mayúsculas, espacios, guiones)',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]  # Guardar solo los primeros 20 para el reporte
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} problemas de normalización")
