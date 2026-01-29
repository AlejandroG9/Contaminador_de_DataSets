"""
CASO 2: Validación de Rangos Numéricos
Introduce valores fuera de rango en columnas numéricas:
- Edades fuera del rango 18-22
- Tiempo de pantalla > 24 horas
- Scores fuera de rangos válidos
- Valores negativos donde no aplican
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso2(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce valores fuera de rango en columnas numéricas.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 2: Validación de Rangos Numéricos ===")
    problemas_introducidos = []
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
    
    # Age: valores fuera de rango 18-22
    for idx in indices[:num_contaminar//4]:
        valor_contaminado = random.choice([0, 15, 17, 23, 25, 30, 100])
        valor_original = df.at[idx, 'Age']
        df.at[idx, 'Age'] = valor_contaminado
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'Age',
            'valor_original': valor_original,
            'valor_contaminado': valor_contaminado,
            'problema': 'Valor fuera de rango válido (18-22)'
        })
    
    # Daily_Screen_Time_Hours: valores > 24 o negativos
    for idx in indices[num_contaminar//4:num_contaminar//2]:
        valor_contaminado = random.choice([-5.5, 25.0, 30.5, 48.0])
        valor_original = df.at[idx, 'Daily_Screen_Time_Hours']
        df.at[idx, 'Daily_Screen_Time_Hours'] = valor_contaminado
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'Daily_Screen_Time_Hours',
            'valor_original': valor_original,
            'valor_contaminado': valor_contaminado,
            'problema': 'Valor fuera de rango lógico (>24 horas o negativo)'
        })
    
    # GAD_7_Score: valores fuera de rango 0-21
    for idx in indices[num_contaminar//2:3*num_contaminar//4]:
        valor_contaminado = random.choice([-1, 22, 25, 30])
        valor_original = df.at[idx, 'GAD_7_Score']
        df.at[idx, 'GAD_7_Score'] = valor_contaminado
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'GAD_7_Score',
            'valor_original': valor_original,
            'valor_contaminado': valor_contaminado,
            'problema': 'Valor fuera de rango válido (0-21)'
        })
    
    # PHQ_9_Score: valores fuera de rango 0-27
    for idx in indices[3*num_contaminar//4:]:
        valor_contaminado = random.choice([-2, 28, 30, 35])
        valor_original = df.at[idx, 'PHQ_9_Score']
        df.at[idx, 'PHQ_9_Score'] = valor_contaminado
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'PHQ_9_Score',
            'valor_original': valor_original,
            'valor_contaminado': valor_contaminado,
            'problema': 'Valor fuera de rango válido (0-27)'
        })
    
    reporte_problemas['caso2_validacion_rangos'] = {
        'descripcion': 'Valores numéricos fuera de rangos válidos o lógicos',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} valores fuera de rango")
