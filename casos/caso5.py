"""
CASO 5: Manejo de Valores Faltantes
Introduce valores faltantes de diferentes formas:
- Celdas vacías
- Valores como "N/A", "NULL", "NaN", etc.
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso5(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce valores faltantes de diferentes formas.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 5: Manejo de Valores Faltantes ===")
    problemas_introducidos = []
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    
    # Valores faltantes comunes
    valores_faltantes = ['', 'N/A', 'NULL', 'NaN', 'null', 'na', 'N/A', '?', '-']
    
    # Seleccionar columnas para introducir valores faltantes
    columnas_objetivo = ['Age', 'Gender', 'Primary_Platform', 'Daily_Screen_Time_Hours', 
                        'Sleep_Duration_Hours', 'GAD_7_Score', 'PHQ_9_Score']
    
    for columna in columnas_objetivo:
        if columna not in df.columns:
            continue
            
        indices = random.sample(range(num_registros), min(num_contaminar//len(columnas_objetivo), num_registros))
        
        for idx in indices:
            valor_original = df.at[idx, columna]
            valor_faltante = random.choice(valores_faltantes)
            df.at[idx, columna] = valor_faltante
            problemas_introducidos.append({
                'indice': idx,
                'columna': columna,
                'valor_original': valor_original,
                'valor_faltante': valor_faltante,
                'problema': f'Valor faltante representado como: {valor_faltante}'
            })
    
    reporte_problemas['caso5_valores_faltantes'] = {
        'descripcion': 'Valores faltantes (vacíos, N/A, NULL, etc.)',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} valores faltantes")
