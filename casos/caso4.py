"""
CASO 4: Validación de Consistencia entre Columnas
Introduce inconsistencias entre columnas relacionadas:
- GAD_7_Score vs GAD_7_Severity
- PHQ_9_Score vs PHQ_9_Severity
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso4(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce inconsistencias entre columnas relacionadas.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 4: Validación de Consistencia entre Columnas ===")
    problemas_introducidos = []
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
    
    # Mapeo de scores a severidades esperadas
    def get_gad_severity(score):
        if score <= 4:
            return 'Minimal'
        elif score <= 9:
            return 'Mild'
        elif score <= 14:
            return 'Moderate'
        else:
            return 'Severe'
    
    def get_phq_severity(score):
        if score <= 4:
            return 'None-Minimal'
        elif score <= 9:
            return 'Mild'
        elif score <= 14:
            return 'Moderate'
        elif score <= 19:
            return 'Moderately Severe'
        else:
            return 'Severe'
    
    # GAD_7: Cambiar severidad a una incorrecta
    for idx in indices[:num_contaminar//2]:
        score = int(df.at[idx, 'GAD_7_Score'])
        severidad_correcta = get_gad_severity(score)
        severidades_incorrectas = [s for s in ['Minimal', 'Mild', 'Moderate', 'Severe'] if s != severidad_correcta]
        severidad_contaminada = random.choice(severidades_incorrectas)
        
        valor_original = df.at[idx, 'GAD_7_Severity']
        df.at[idx, 'GAD_7_Severity'] = severidad_contaminada
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'GAD_7_Severity',
            'score': score,
            'severidad_correcta': severidad_correcta,
            'severidad_contaminada': severidad_contaminada,
            'problema': f'Inconsistencia: Score {score} debería ser {severidad_correcta}, pero es {severidad_contaminada}'
        })
    
    # PHQ_9: Cambiar severidad a una incorrecta
    for idx in indices[num_contaminar//2:]:
        score = int(df.at[idx, 'PHQ_9_Score'])
        severidad_correcta = get_phq_severity(score)
        severidades_incorrectas = [s for s in ['None-Minimal', 'Mild', 'Moderate', 'Moderately Severe', 'Severe'] if s != severidad_correcta]
        severidad_contaminada = random.choice(severidades_incorrectas)
        
        valor_original = df.at[idx, 'PHQ_9_Severity']
        df.at[idx, 'PHQ_9_Severity'] = severidad_contaminada
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'PHQ_9_Severity',
            'score': score,
            'severidad_correcta': severidad_correcta,
            'severidad_contaminada': severidad_contaminada,
            'problema': f'Inconsistencia: Score {score} debería ser {severidad_correcta}, pero es {severidad_contaminada}'
        })
    
    reporte_problemas['caso4_consistencia'] = {
        'descripcion': 'Inconsistencias entre scores y severidades',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidas {len(problemas_introducidos)} inconsistencias entre columnas")
