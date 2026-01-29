"""
CASO 3: Detección de Outliers
Introduce outliers estadísticamente extremos pero técnicamente válidos:
- Tiempos de pantalla muy altos (pero < 24 horas)
- Duraciones de sueño extremas (pero dentro de límites físicos)
"""

import random
import pandas as pd
from typing import Dict


def aplicar_caso3(df: pd.DataFrame, porcentaje_contaminacion: float, reporte_problemas: Dict) -> None:
    """
    Introduce outliers estadísticamente extremos pero técnicamente válidos.
    
    Args:
        df: DataFrame a contaminar
        porcentaje_contaminacion: Porcentaje de registros a contaminar
        reporte_problemas: Diccionario donde se guardarán los problemas introducidos
    """
    print("\n=== CASO 3: Detección de Outliers ===")
    problemas_introducidos = []
    
    num_registros = len(df)
    num_contaminar = int(num_registros * porcentaje_contaminacion)
    indices = random.sample(range(num_registros), min(num_contaminar, num_registros))
    
    # Calcular estadísticas para identificar outliers
    screen_time_mean = df['Daily_Screen_Time_Hours'].mean()
    screen_time_std = df['Daily_Screen_Time_Hours'].std()
    sleep_mean = df['Sleep_Duration_Hours'].mean()
    sleep_std = df['Sleep_Duration_Hours'].std()
    
    # Daily_Screen_Time_Hours: valores extremadamente altos (pero < 24)
    for idx in indices[:num_contaminar//2]:
        # Valores > 3 desviaciones estándar pero < 24 horas
        valor_contaminado = min(23.5, screen_time_mean + random.uniform(3.5, 5) * screen_time_std)
        valor_original = df.at[idx, 'Daily_Screen_Time_Hours']
        df.at[idx, 'Daily_Screen_Time_Hours'] = round(valor_contaminado, 2)
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'Daily_Screen_Time_Hours',
            'valor_original': round(valor_original, 2),
            'valor_contaminado': round(valor_contaminado, 2),
            'problema': 'Outlier estadístico (valor extremo pero técnicamente válido)'
        })
    
    # Sleep_Duration_Hours: valores extremos
    for idx in indices[num_contaminar//2:]:
        # Valores muy altos o muy bajos pero físicamente posibles
        if random.random() > 0.5:
            valor_contaminado = min(12.0, sleep_mean + random.uniform(3, 4) * sleep_std)
        else:
            valor_contaminado = max(1.5, sleep_mean - random.uniform(3, 4) * sleep_std)
        valor_original = df.at[idx, 'Sleep_Duration_Hours']
        df.at[idx, 'Sleep_Duration_Hours'] = round(valor_contaminado, 2)
        problemas_introducidos.append({
            'indice': idx,
            'columna': 'Sleep_Duration_Hours',
            'valor_original': round(valor_original, 2),
            'valor_contaminado': round(valor_contaminado, 2),
            'problema': 'Outlier estadístico (valor extremo pero técnicamente válido)'
        })
    
    reporte_problemas['caso3_outliers'] = {
        'descripcion': 'Outliers estadísticamente extremos pero técnicamente válidos',
        'total_problemas': len(problemas_introducidos),
        'problemas': problemas_introducidos[:20]
    }
    print(f"  ✓ Introducidos {len(problemas_introducidos)} outliers")
